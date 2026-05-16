using System.Numerics;
using HollowDemo.Game;
using Raylib_cs;

namespace HollowDemo.Enemies;

/// <summary>
/// Husk / наземный патрульный: бегает по платформе, разворачивается на краю.
/// </summary>
public sealed class PatrolStrategy : IEnemyStrategy
{
    public string Name => "Patrol";
    private const float Speed = 80f;
    private float _edgeProbeCooldown;

    public void Update(Enemy e, Player.Player player, Scene scene, float dt)
    {
        e.Velocity.X = e.Facing * Speed;

        // Каждые ~0.2 сек проверяем «есть ли пол на 4 пикселя впереди ноги».
        _edgeProbeCooldown -= dt;
        if (_edgeProbeCooldown <= 0)
        {
            _edgeProbeCooldown = 0.15f;
            float probeX = e.Facing > 0 ? e.Position.X + e.Size.X + 4 : e.Position.X - 4;
            float probeY = e.Position.Y + e.Size.Y + 2;
            bool floorAhead = false;
            foreach (var plat in scene.ObjectsOf<Platform>())
            {
                if (plat.Bounds.X <= probeX && probeX <= plat.Bounds.X + plat.Bounds.Width
                    && plat.Bounds.Y <= probeY && probeY <= plat.Bounds.Y + 4)
                {
                    floorAhead = true; break;
                }
            }
            if (!floorAhead) e.Facing *= -1;
        }
    }
}

/// <summary>
/// Vengefly / летающий преследователь: игнорирует гравитацию и
/// медленно подплывает к игроку по прямой. Скорость заметно ниже,
/// чем у игрока в беге (60 против 220), — он успевает ударить
/// гвоздём первым.
/// </summary>
public sealed class ChaseStrategy : IEnemyStrategy
{
    public string Name => "Chase";
    private const float Speed = 60f;

    public void Update(Enemy e, Player.Player player, Scene scene, float dt)
    {
        Vector2 playerCenter = new(player.Position.X + player.Size.X / 2,
                                   player.Position.Y + player.Size.Y / 2);
        Vector2 enemyCenter  = new(e.Position.X + e.Size.X / 2,
                                   e.Position.Y + e.Size.Y / 2);
        Vector2 toPlayer = playerCenter - enemyCenter;
        float dist = toPlayer.Length();
        if (dist > 1f)
        {
            e.Velocity = (toPlayer / dist) * Speed;
        }
        else
        {
            e.Velocity = Vector2.Zero;
        }
        e.Facing = toPlayer.X >= 0 ? 1 : -1;
    }
}

/// <summary>
/// Archer / стрелок: стоит на месте, периодически плюёт снарядом в игрока.
/// </summary>
public sealed class RangedStrategy : IEnemyStrategy
{
    public string Name => "Ranged";
    private float _cooldown;
    private const float Cooldown = 1.8f;

    public void Update(Enemy e, Player.Player player, Scene scene, float dt)
    {
        e.Velocity.X = 0;
        e.Facing = player.Position.X < e.Position.X ? -1 : 1;
        _cooldown -= dt;
        if (_cooldown <= 0)
        {
            _cooldown = Cooldown;
            var origin = new Vector2(e.Position.X + e.Size.X / 2, e.Position.Y + 12);
            var aim = Vector2.Normalize(
                new Vector2(player.Position.X + player.Size.X / 2,
                            player.Position.Y + player.Size.Y / 2) - origin);
            scene.Add(new Projectile(origin, aim * 240f));
        }
    }
}
