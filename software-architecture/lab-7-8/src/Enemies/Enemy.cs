using System.Numerics;
using HollowDemo.Events;
using HollowDemo.Game;
using Raylib_cs;

namespace HollowDemo.Enemies;

/// <summary>
/// Базовый класс врага. Сам по себе мало что умеет — поведение
/// (патруль / преследование / стрельба) делегируется стратегии,
/// а состояние (живой / получает урон / мертвец) — простому enum'у.
///
/// Конкретные типы (HuskEnemy, FlyEnemy, ArcherEnemy) отличаются только
/// своей стратегией и текстурой; их создаёт EnemyFactory.
/// </summary>
public sealed class Enemy : GameObject
{
    public enum EnemyState { Alive, Hurt, Dead }

    public Texture2D Texture;
    public IEnemyStrategy Strategy;
    public int Hp;
    public int Damage;
    public int Id { get; }
    public int Facing = -1;
    public Vector2 Velocity;
    public EnemyState State { get; private set; } = EnemyState.Alive;
    public float Gravity = 1400f;
    public bool UseGravity = true;
    public bool IsGrounded;
    public string Kind { get; }
    // Размер «реального» хитбокса (без прозрачной обводки спрайта),
    // используется для контактного урона и проверки попадания гвоздём.
    public Vector2 HitBoxSize;
    public Vector2 HitBoxOffset;
    public Rectangle HitBox => new(
        Position.X + HitBoxOffset.X, Position.Y + HitBoxOffset.Y,
        HitBoxSize.X, HitBoxSize.Y);

    private float _hurtTimer;
    private float _animTime;
    private static int _nextId;

    public Enemy(string kind, Vector2 spawn, Vector2 size, Texture2D tex,
                 IEnemyStrategy strategy, int hp, int damage, bool useGravity = true,
                 Vector2? hitBoxSize = null, Vector2? hitBoxOffset = null)
        : base(spawn, size)
    {
        Kind = kind;
        Texture = tex;
        Strategy = strategy;
        Hp = hp;
        Damage = damage;
        UseGravity = useGravity;
        HitBoxSize = hitBoxSize ?? size;
        HitBoxOffset = hitBoxOffset ?? Vector2.Zero;
        Id = ++_nextId;
    }

    public override void Update(float dt, Scene scene)
    {
        _animTime += dt;
        if (State == EnemyState.Dead) return;

        if (State == EnemyState.Hurt)
        {
            _hurtTimer -= dt;
            if (UseGravity) Velocity.Y += Gravity * dt;
            ApplyMovement(dt, scene);
            if (_hurtTimer <= 0) State = EnemyState.Alive;
            return;
        }

        if (scene.Player is not null)
        {
            Strategy.Update(this, scene.Player, scene, dt);
        }
        if (UseGravity) Velocity.Y += Gravity * dt;
        ApplyMovement(dt, scene);

        // Контактный урон — только при пересечении хитбоксов (а не
        // полных спрайтов): иначе срабатывает на прозрачных пикселях.
        if (scene.Player is { } p && Raylib.CheckCollisionRecs(HitBox, p.HitBox))
        {
            p.TakeHit(Position);
        }
    }

    public override void Draw()
    {
        Color tint = State == EnemyState.Hurt && (int)(_animTime * 16) % 2 == 0
            ? new Color(255, 80, 80, 255) : Color.White;
        var src = new Rectangle(0, 0, Facing >= 0 ? Texture.Width : -Texture.Width, Texture.Height);
        var dst = new Rectangle(Position.X, Position.Y, Size.X, Size.Y);
        Raylib.DrawTexturePro(Texture, src, dst, Vector2.Zero, 0, tint);
    }

    public void TakeDamage(int amount)
    {
        if (State == EnemyState.Dead) return;
        Hp -= amount;
        if (Hp <= 0)
        {
            State = EnemyState.Dead;
            Kill();
            GameEvents.RaiseEnemyDied(Id);
        }
        else
        {
            State = EnemyState.Hurt;
            _hurtTimer = 0.25f;
            Velocity.X = -Facing * 120; // лёгкий нокбэк
        }
    }

    public void ApplyMovement(float dt, Scene scene)
    {
        Position = Position with { X = Position.X + Velocity.X * dt };
        ResolveAxis(scene, axisX: true);
        Position = Position with { Y = Position.Y + Velocity.Y * dt };
        IsGrounded = false;
        ResolveAxis(scene, axisX: false);
    }

    private void ResolveAxis(Scene scene, bool axisX)
    {
        foreach (var plat in scene.ObjectsOf<Platform>())
        {
            if (!Raylib.CheckCollisionRecs(Bounds, plat.Bounds)) continue;
            if (axisX)
            {
                if (Velocity.X > 0) Position = Position with { X = plat.Position.X - Size.X };
                else if (Velocity.X < 0) Position = Position with { X = plat.Position.X + plat.Size.X };
                Velocity.X = 0;
            }
            else
            {
                if (Velocity.Y > 0) { Position = Position with { Y = plat.Position.Y - Size.Y }; IsGrounded = true; }
                else if (Velocity.Y < 0) Position = Position with { Y = plat.Position.Y + plat.Size.Y };
                Velocity.Y = 0;
            }
        }
    }
}
