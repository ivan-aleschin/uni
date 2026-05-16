using System.Numerics;
using HollowDemo.Enemies;
using HollowDemo.Events;
using HollowDemo.Game;
using Raylib_cs;

namespace HollowDemo.Player;

/// <summary>
/// ConcreteSubject (для Observer) и владелец конечного автомата (для State).
/// Содержит ссылку на текущее IPlayerState и делегирует ему всё поведение.
/// Сам класс остаётся тонким — никаких больших switch/if по состояниям.
/// </summary>
public sealed class Player : GameObject
{
    public const float RunSpeed = 220f;
    public const float JumpVelocity = 480f;
    public const float Gravity = 1400f;
    public const float DashSpeed = 600f;
    public const float DashDuration = 0.18f;
    public const float AttackDuration = 0.22f;
    public const float HurtDuration = 0.35f;
    public const int MaxHp = 5;
    public const int MaxSoul = 99;
    public const int SoulPerHit = 11;
    public const int SoulPerHeal = 33;

    public Vector2 Velocity;
    public int Facing = 1;
    public bool IsGrounded;
    public bool IsInvincible;
    // Хитбокс игрока (≈18×40) — меньше визуального спрайта 32×48.
    public Rectangle HitBox => new(Position.X + 7, Position.Y + 8, 18, 40);
    public int Hp { get; private set; } = MaxHp;
    public int Soul { get; private set; }
    public int Kills { get; private set; }

    public IPlayerState State { get; private set; } = new IdleState();

    // Анимация
    public static Texture2D TexIdle, TexRunA, TexRunB, TexJump, TexAttack, TexSlash;
    private float _animTime;

    public Player(Vector2 spawnPosition)
        : base(spawnPosition, new Vector2(32, 48))
    {
        State.Enter(this);
    }

    public void ChangeState(IPlayerState next)
    {
        State.Exit(this);
        State = next;
        State.Enter(this);
    }

    public override void Update(float dt, Scene scene)
    {
        _animTime += dt;
        if (State is DeadState) return;
        State.HandleInput(this);
        State.Update(this, dt, scene);
        // Падение за карту — мгновенная смерть.
        if (Position.Y > scene.DeathY)
        {
            Hp = 0;
            GameEvents.RaisePlayerHpChanged(Hp, MaxHp);
            ChangeState(new DeadState());
        }
    }

    public override void Draw()
    {
        Texture2D tex = TexIdle;
        switch (State.Name)
        {
            case "Run":
                tex = ((int)(_animTime * 8) % 2 == 0) ? TexRunA : TexRunB; break;
            case "Jump":
            case "DoubleJump":
                tex = TexJump; break;
            case "Attack":
                tex = TexAttack; break;
            case "Dash":
                tex = TexJump; break; // используем jump-силуэт для дэша
            case "Hurt":
                if ((int)(_animTime * 16) % 2 == 0) return; // мигание
                tex = TexIdle; break;
            case "Dead":
                tex = TexIdle; break;
        }
        var source = new Rectangle(0, 0, Facing >= 0 ? tex.Width : -tex.Width, tex.Height);
        var dest = new Rectangle(Position.X, Position.Y, Size.X, Size.Y);
        Raylib.DrawTexturePro(tex, source, dest, Vector2.Zero, 0, Color.White);

        // Слэш — отдельный спрайт, рисуется поверх во время AttackState
        // и охватывает по высоте всего игрока (и чуть выше макушки).
        if (State is AttackState)
        {
            var slashSrc = new Rectangle(0, 0,
                Facing >= 0 ? TexSlash.Width : -TexSlash.Width, TexSlash.Height);
            // Дуга высотой 56 px, верхняя точка на 4 px выше макушки.
            float slashY = Position.Y - 4;
            float slashX = Facing >= 0 ? Position.X + Size.X - 6 : Position.X - 22;
            var slashDst = new Rectangle(slashX, slashY, 28, 56);
            Raylib.DrawTexturePro(TexSlash, slashSrc, slashDst, Vector2.Zero, 0, Color.White);
        }
    }

    // ---------- Физика и взаимодействия ----------

    public void ApplyGravity(float dt) => Velocity = Velocity with { Y = Velocity.Y + Gravity * dt };

    public void ApplyMovement(float dt, Scene scene)
    {
        // Сначала сдвигаем по X, проверяем коллизии с платформами.
        Position = Position with { X = Position.X + Velocity.X * dt };
        ResolveAxis(scene, axisX: true);
        // Потом по Y.
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
                Velocity = Velocity with { X = 0 };
            }
            else
            {
                if (Velocity.Y > 0)
                {
                    Position = Position with { Y = plat.Position.Y - Size.Y };
                    IsGrounded = true;
                }
                else if (Velocity.Y < 0)
                {
                    Position = Position with { Y = plat.Position.Y + plat.Size.Y };
                }
                Velocity = Velocity with { Y = 0 };
            }
        }
    }

    public void DealNailDamage(Scene scene)
    {
        // «Гвоздь» — взмах снизу-вверх, охватывает всю высоту игрока
        // (от чуть ниже ног до выше макушки), ширина ≈22 px рядом с телом.
        var nail = new Rectangle(
            Facing >= 0 ? Position.X + Size.X - 6 : Position.X - 16,
            Position.Y - 4, 22, Size.Y + 8);
        foreach (var enemy in scene.ObjectsOf<Enemy>())
        {
            if (!enemy.IsAlive) continue;
            // Бьём по hitbox'у, а не по полному bounds — иначе попадаем
            // в прозрачные пиксели вокруг силуэта.
            if (!Raylib.CheckCollisionRecs(nail, enemy.HitBox)) continue;
            bool wasAlive = enemy.State != Enemy.EnemyState.Dead;
            enemy.TakeDamage(1);
            GainSoul(SoulPerHit);
            if (wasAlive && enemy.State == Enemy.EnemyState.Dead)
                OnEnemyKilled();
        }
    }

    public void GainSoul(int amount)
    {
        Soul = Math.Min(Soul + amount, MaxSoul);
        GameEvents.RaisePlayerSoulChanged(Soul, MaxSoul);
    }

    public void TryFocusHeal()
    {
        if (Soul < SoulPerHeal || Hp >= MaxHp) return;
        Soul -= SoulPerHeal;
        Hp = Math.Min(Hp + 1, MaxHp);
        GameEvents.RaisePlayerHpChanged(Hp, MaxHp);
        GameEvents.RaisePlayerSoulChanged(Soul, MaxSoul);
    }

    public void TakeHit(Vector2 from)
    {
        if (IsInvincible || State is DeadState) return;
        Hp--;
        GameEvents.RaisePlayerHpChanged(Hp, MaxHp);
        if (Hp <= 0) { ChangeState(new DeadState()); return; }
        // Отбрасывание в сторону, противоположную врагу.
        int knockDir = Position.X < from.X ? -1 : 1;
        Velocity = new Vector2(knockDir * 220, -260);
        ChangeState(new HurtState());
    }

    public void OnEnemyKilled()
    {
        Kills++;
        GameEvents.RaisePlayerScoredKill(Kills);
    }
}
