using System.Numerics;
using Raylib_cs;

namespace HollowDemo.Game;

/// <summary>
/// Статичный тайл-платформа. Лист композиции (Leaf): сама ничего не
/// обновляет, только рисует свою тайл-текстуру по ширине.
/// </summary>
public sealed class Platform : GameObject
{
    // Два тайла: верхний ряд — травяной, нижние — земля.
    public static Texture2D GrassTexture;
    public static Texture2D DirtTexture;
    private readonly int _tilesWide;
    private readonly int _tilesHigh;

    public Platform(Vector2 position, int tilesWide, int tilesHigh = 1)
        : base(position, new Vector2(tilesWide * 32, tilesHigh * 32))
    {
        _tilesWide = tilesWide;
        _tilesHigh = tilesHigh;
    }

    public override void Update(float dt, Scene scene) { }

    public override void Draw()
    {
        for (int x = 0; x < _tilesWide; x++)
        {
            for (int y = 0; y < _tilesHigh; y++)
            {
                Texture2D tex = y == 0 ? GrassTexture : DirtTexture;
                Raylib.DrawTextureV(tex,
                    new Vector2(Position.X + x * 32, Position.Y + y * 32),
                    Color.White);
            }
        }
    }
}
