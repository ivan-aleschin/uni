using System.Numerics;
using HollowDemo.Enemies;
using HollowDemo.Events;
using HollowDemo.Game;
using HollowDemo.UI;
using Raylib_cs;

const int InitialWidth = 1280;
const int InitialHeight = 720;

Font _uiFont = default;
Texture2D _bgFar = default, _bgMid = default, _bgNear = default, _bgStars = default;

Raylib.SetConfigFlags(ConfigFlags.ResizableWindow | ConfigFlags.VSyncHint);
Raylib.InitWindow(InitialWidth, InitialHeight, "HollowDemo — лаба 7-8");
Raylib.SetTargetFPS(60);

LoadAssets();
Hud.Font = _uiFont;
GameOverScreen.Font = _uiFont;

var (scene, hud, gameOver) = BuildLevel();

var camera = new Camera2D
{
    Offset = new Vector2(InitialWidth / 2f, InitialHeight / 2f),
    Target = new Vector2(scene.Player!.Position.X + 16, scene.Player!.Position.Y + 24),
    Rotation = 0f,
    Zoom = 2.5f
};

while (!Raylib.WindowShouldClose())
{
    float dt = Raylib.GetFrameTime();

    if (Raylib.IsKeyPressed(KeyboardKey.F11)
        || (Raylib.IsKeyPressed(KeyboardKey.Enter) && Raylib.IsKeyDown(KeyboardKey.LeftAlt)))
        Raylib.ToggleFullscreen();

    camera.Offset = new Vector2(Raylib.GetScreenWidth() / 2f, Raylib.GetScreenHeight() / 2f);

    if (!gameOver.IsActive)
    {
        scene.Update(dt);
        var p = scene.Player!;
        var target = new Vector2(p.Position.X + p.Size.X / 2f, p.Position.Y + p.Size.Y / 2f);
        camera.Target = Vector2.Lerp(camera.Target, target, MathF.Min(1f, 5f * dt));
        ClampCameraToWorld(ref camera, scene.WorldBounds);
    }
    else if (Raylib.IsKeyPressed(KeyboardKey.R))
    {
        hud.Dispose();
        gameOver.Dispose();
        GameEvents.ClearAllSubscribers();
        (scene, hud, gameOver) = BuildLevel();
        camera.Target = new Vector2(scene.Player!.Position.X + 16, scene.Player!.Position.Y + 24);
    }

    Raylib.BeginDrawing();
    Raylib.ClearBackground(new Color(20, 20, 36, 255));
    DrawParallaxBackdrop(camera);

    Raylib.BeginMode2D(camera);
    scene.Draw();
    Raylib.EndMode2D();

    hud.Draw();
    gameOver.Draw();
    // Подсказка управления — рисуем шрифтом с кириллицей.
    string hint = "WASD / ← → — бег   Space — прыжок (×2)   Shift — dash   J / ЛКМ — атака   K — heal   F11 — fullscreen";
    Raylib.DrawTextEx(_uiFont, hint, new Vector2(12, Raylib.GetScreenHeight() - 26),
        18, 0, new Color(210, 210, 230, 230));
    Raylib.EndDrawing();
}

UnloadAssets();
Raylib.CloseWindow();
return;

// ---------------- helpers ----------------

(Scene, Hud, GameOverScreen) BuildLevel()
{
    var scene = new Scene
    {
        WorldBounds = new Rectangle(-200, -200, 2200, 1300),
        DeathY = 900
    };

    // Левый пол (3 ряда — видна толщина земли).
    scene.Add(new Platform(new Vector2(0,   640), tilesWide: 14, tilesHigh: 3));
    // Правый пол.
    scene.Add(new Platform(new Vector2(640, 640), tilesWide: 22, tilesHigh: 3));
    // Парящие платформы — по одному ряду, как травяные островки.
    scene.Add(new Platform(new Vector2(360,  548), tilesWide: 4));
    scene.Add(new Platform(new Vector2(720,  548), tilesWide: 5));
    scene.Add(new Platform(new Vector2(1040, 500), tilesWide: 4));
    scene.Add(new Platform(new Vector2(160,  460), tilesWide: 3));

    var player = new HollowDemo.Player.Player(new Vector2(60, 580));
    scene.Player = player;
    scene.Add(player);

    scene.Add(EnemyFactory.Spawn(EnemyFactory.EnemyKind.Husk,   new Vector2(300, 608)));
    scene.Add(EnemyFactory.Spawn(EnemyFactory.EnemyKind.Husk,   new Vector2(880, 608)));
    scene.Add(EnemyFactory.Spawn(EnemyFactory.EnemyKind.Fly,    new Vector2(560, 420)));
    scene.Add(EnemyFactory.Spawn(EnemyFactory.EnemyKind.Fly,    new Vector2(940, 380)));
    scene.Add(EnemyFactory.Spawn(EnemyFactory.EnemyKind.Archer, new Vector2(1080, 468)));

    var hud = new Hud();
    var gameOver = new GameOverScreen();

    GameEvents.RaisePlayerHpChanged(player.Hp, HollowDemo.Player.Player.MaxHp);
    GameEvents.RaisePlayerSoulChanged(player.Soul, HollowDemo.Player.Player.MaxSoul);
    GameEvents.RaisePlayerScoredKill(0);
    return (scene, hud, gameOver);
}

void ClampCameraToWorld(ref Camera2D cam, Rectangle world)
{
    float halfW = Raylib.GetScreenWidth() / (2f * cam.Zoom);
    float halfH = Raylib.GetScreenHeight() / (2f * cam.Zoom);
    cam.Target = new Vector2(
        Math.Clamp(cam.Target.X, world.X + halfW, world.X + world.Width  - halfW),
        Math.Clamp(cam.Target.Y, world.Y + halfH, world.Y + world.Height - halfH));
}

void DrawParallaxBackdrop(Camera2D cam)
{
    int sw = Raylib.GetScreenWidth();
    int sh = Raylib.GetScreenHeight();
    // Базовый градиент (на случай, если слой не покрывает весь экран).
    Raylib.DrawRectangleGradientV(0, 0, sw, sh,
        new Color(38, 28, 60, 255), new Color(10, 8, 22, 255));
    // 4 слоя в порядке от дальнего к ближнему. Каждый сдвигается
    // относительно камеры со своим коэффициентом — это и есть parallax.
    DrawParallaxLayer(_bgFar,   cam, 0.05f, sw, sh);
    DrawParallaxLayer(_bgStars, cam, 0.10f, sw, sh);
    DrawParallaxLayer(_bgMid,   cam, 0.25f, sw, sh);
    DrawParallaxLayer(_bgNear,  cam, 0.50f, sw, sh);
}

void DrawParallaxLayer(Texture2D tex, Camera2D cam, float factor, int sw, int sh)
{
    // Слой растягиваем на экран; смещение по X — функция от камеры.
    float scrollX = -(cam.Target.X * factor) % tex.Width;
    var src = new Rectangle(0, 0, tex.Width, tex.Height);
    var dst1 = new Rectangle(scrollX,             0, sw, sh);
    var dst2 = new Rectangle(scrollX + sw,        0, sw, sh);
    var dst3 = new Rectangle(scrollX - sw,        0, sw, sh);
    Raylib.DrawTexturePro(tex, src, dst1, Vector2.Zero, 0, Color.White);
    Raylib.DrawTexturePro(tex, src, dst2, Vector2.Zero, 0, Color.White);
    Raylib.DrawTexturePro(tex, src, dst3, Vector2.Zero, 0, Color.White);
}

// ---- загрузка ассетов ----

void LoadAssets()
{
    string a = Path.Combine(AppContext.BaseDirectory, "assets");

    HollowDemo.Player.Player.TexIdle   = Tex(Path.Combine(a, "player_idle.png"));
    HollowDemo.Player.Player.TexRunA   = Tex(Path.Combine(a, "player_run_a.png"));
    HollowDemo.Player.Player.TexRunB   = Tex(Path.Combine(a, "player_run_b.png"));
    HollowDemo.Player.Player.TexJump   = Tex(Path.Combine(a, "player_jump.png"));
    HollowDemo.Player.Player.TexAttack = Tex(Path.Combine(a, "player_attack.png"));
    HollowDemo.Player.Player.TexSlash  = Tex(Path.Combine(a, "player_slash.png"));
    EnemyFactory.TexHusk   = Tex(Path.Combine(a, "enemy_husk.png"));
    EnemyFactory.TexFly    = Tex(Path.Combine(a, "enemy_fly.png"));
    EnemyFactory.TexArcher = Tex(Path.Combine(a, "enemy_archer.png"));
    Platform.GrassTexture  = Tex(Path.Combine(a, "tile.png"));
    Platform.DirtTexture   = Tex(Path.Combine(a, "tile_dirt.png"));
    Projectile.Texture     = Tex(Path.Combine(a, "projectile.png"));

    _bgFar   = Tex(Path.Combine(a, "background_far.png"));
    _bgStars = Tex(Path.Combine(a, "background_stars.png"));
    _bgMid   = Tex(Path.Combine(a, "background_mid.png"));
    _bgNear  = Tex(Path.Combine(a, "background_near.png"));

    // Шрифт с поддержкой кириллицы. Загружаем явный набор кодпойнтов:
    // ASCII + расширенная кириллица. Без этого DrawTextEx показывает «?»
    // на местах букв «бег», «прыжок» и т. д.
    var cps = new List<int>();
    for (int c = 32;     c < 127;   c++) cps.Add(c);   // ASCII
    for (int c = 0x0400; c <= 0x045F; c++) cps.Add(c); // основная кириллица + расширения
    cps.Add(0x2014);                                   // —
    cps.Add(0x00AB); cps.Add(0x00BB);                  // « »
    cps.Add(0x00D7); cps.Add(0x2192); cps.Add(0x2190); // × → ←
    _uiFont = Raylib.LoadFontEx(Path.Combine(a, "font.ttf"), 22, cps.ToArray(), cps.Count);
}

Texture2D Tex(string path)
{
    var t = Raylib.LoadTexture(path);
    Raylib.SetTextureFilter(t, TextureFilter.Point);
    return t;
}

void UnloadAssets()
{
    Raylib.UnloadTexture(HollowDemo.Player.Player.TexIdle);
    Raylib.UnloadTexture(HollowDemo.Player.Player.TexRunA);
    Raylib.UnloadTexture(HollowDemo.Player.Player.TexRunB);
    Raylib.UnloadTexture(HollowDemo.Player.Player.TexJump);
    Raylib.UnloadTexture(HollowDemo.Player.Player.TexAttack);
    Raylib.UnloadTexture(HollowDemo.Player.Player.TexSlash);
    Raylib.UnloadTexture(EnemyFactory.TexHusk);
    Raylib.UnloadTexture(EnemyFactory.TexFly);
    Raylib.UnloadTexture(EnemyFactory.TexArcher);
    Raylib.UnloadTexture(Platform.GrassTexture);
    Raylib.UnloadTexture(Platform.DirtTexture);
    Raylib.UnloadTexture(Projectile.Texture);
    Raylib.UnloadTexture(_bgFar);
    Raylib.UnloadTexture(_bgStars);
    Raylib.UnloadTexture(_bgMid);
    Raylib.UnloadTexture(_bgNear);
    Raylib.UnloadFont(_uiFont);
}
