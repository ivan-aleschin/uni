using HollowDemo.Game;
using Raylib_cs;

namespace HollowDemo.Player;

// ---------- Idle ----------
public sealed class IdleState : IPlayerState
{
    public string Name => "Idle";
    public void Enter(Player p) { p.Velocity = p.Velocity with { X = 0 }; }
    public void HandleInput(Player p)
    {
        if (Raylib.IsKeyDown(KeyboardKey.A) || Raylib.IsKeyDown(KeyboardKey.D)
            || Raylib.IsKeyDown(KeyboardKey.Left) || Raylib.IsKeyDown(KeyboardKey.Right))
        {
            p.ChangeState(new RunState());
            return;
        }
        if (Raylib.IsKeyPressed(KeyboardKey.Space)) { p.ChangeState(new JumpState()); return; }
        if (Raylib.IsKeyPressed(KeyboardKey.J) || Raylib.IsMouseButtonPressed(MouseButton.Left))
        { p.ChangeState(new AttackState()); return; }
        if (Raylib.IsKeyPressed(KeyboardKey.LeftShift)) { p.ChangeState(new DashState()); return; }
        if (Raylib.IsKeyPressed(KeyboardKey.K)) p.TryFocusHeal();
    }
    public void Update(Player p, float dt, Scene scene)
    {
        p.ApplyGravity(dt); p.ApplyMovement(dt, scene);
        if (!p.IsGrounded) p.ChangeState(new JumpState(midAir: true));
    }
    public void Exit(Player p) { }
}

// ---------- Run ----------
public sealed class RunState : IPlayerState
{
    public string Name => "Run";
    public void Enter(Player p) { }
    public void HandleInput(Player p)
    {
        float dir = 0;
        if (Raylib.IsKeyDown(KeyboardKey.A) || Raylib.IsKeyDown(KeyboardKey.Left)) { dir -= 1; p.Facing = -1; }
        if (Raylib.IsKeyDown(KeyboardKey.D) || Raylib.IsKeyDown(KeyboardKey.Right)) { dir += 1; p.Facing = 1; }
        p.Velocity = p.Velocity with { X = dir * Player.RunSpeed };
        if (dir == 0) { p.ChangeState(new IdleState()); return; }
        if (Raylib.IsKeyPressed(KeyboardKey.Space)) { p.ChangeState(new JumpState()); return; }
        if (Raylib.IsKeyPressed(KeyboardKey.J) || Raylib.IsMouseButtonPressed(MouseButton.Left))
        { p.ChangeState(new AttackState()); return; }
        if (Raylib.IsKeyPressed(KeyboardKey.LeftShift)) { p.ChangeState(new DashState()); return; }
        if (Raylib.IsKeyPressed(KeyboardKey.K)) p.TryFocusHeal();
    }
    public void Update(Player p, float dt, Scene scene)
    {
        p.ApplyGravity(dt); p.ApplyMovement(dt, scene);
        if (!p.IsGrounded) p.ChangeState(new JumpState(midAir: true));
    }
    public void Exit(Player p) { }
}

// ---------- Jump (+ DoubleJump через флаг) ----------
public sealed class JumpState : IPlayerState
{
    private readonly bool _midAirStart; // упали с платформы — двойной прыжок ещё доступен
    private bool _doubleJumpUsed;
    public JumpState(bool midAir = false) { _midAirStart = midAir; }
    public string Name => _doubleJumpUsed ? "DoubleJump" : "Jump";
    public void Enter(Player p)
    {
        if (!_midAirStart) { p.Velocity = p.Velocity with { Y = -Player.JumpVelocity }; }
        _doubleJumpUsed = _midAirStart; // первый прыжок «потрачен» свободным падением
    }
    public void HandleInput(Player p)
    {
        float dir = 0;
        if (Raylib.IsKeyDown(KeyboardKey.A) || Raylib.IsKeyDown(KeyboardKey.Left)) { dir -= 1; p.Facing = -1; }
        if (Raylib.IsKeyDown(KeyboardKey.D) || Raylib.IsKeyDown(KeyboardKey.Right)) { dir += 1; p.Facing = 1; }
        p.Velocity = p.Velocity with { X = dir * Player.RunSpeed };
        if (Raylib.IsKeyPressed(KeyboardKey.Space) && !_doubleJumpUsed)
        { _doubleJumpUsed = true; p.Velocity = p.Velocity with { Y = -Player.JumpVelocity * 0.9f }; }
        if (Raylib.IsKeyPressed(KeyboardKey.LeftShift)) { p.ChangeState(new DashState()); return; }
        if (Raylib.IsKeyPressed(KeyboardKey.J) || Raylib.IsMouseButtonPressed(MouseButton.Left))
        { p.ChangeState(new AttackState(inAir: true)); return; }
    }
    public void Update(Player p, float dt, Scene scene)
    {
        p.ApplyGravity(dt); p.ApplyMovement(dt, scene);
        if (p.IsGrounded)
        {
            if (System.MathF.Abs(p.Velocity.X) > 1f) p.ChangeState(new RunState());
            else p.ChangeState(new IdleState());
        }
    }
    public void Exit(Player p) { }
}

// ---------- Dash ----------
public sealed class DashState : IPlayerState
{
    public string Name => "Dash";
    private float _elapsed;
    public void Enter(Player p)
    {
        _elapsed = 0;
        p.Velocity = new System.Numerics.Vector2(p.Facing * Player.DashSpeed, 0);
        p.IsInvincible = true;
    }
    public void HandleInput(Player p) { /* во время dash управление залочено */ }
    public void Update(Player p, float dt, Scene scene)
    {
        _elapsed += dt;
        p.ApplyMovement(dt, scene); // без гравитации
        if (_elapsed >= Player.DashDuration)
        {
            p.IsInvincible = false;
            p.ChangeState(p.IsGrounded ? new IdleState() : new JumpState(midAir: true));
        }
    }
    public void Exit(Player p) { p.IsInvincible = false; }
}

// ---------- Attack ----------
public sealed class AttackState : IPlayerState
{
    private readonly bool _inAir;
    private float _elapsed;
    private bool _hit;
    public AttackState(bool inAir = false) { _inAir = inAir; }
    public string Name => "Attack";
    public void Enter(Player p) { _elapsed = 0; _hit = false; if (!_inAir) p.Velocity = p.Velocity with { X = 0 }; }
    public void HandleInput(Player p)
    {
        // Во время атаки можно двигаться в воздухе
        if (_inAir)
        {
            float dir = 0;
            if (Raylib.IsKeyDown(KeyboardKey.A) || Raylib.IsKeyDown(KeyboardKey.Left)) dir -= 1;
            if (Raylib.IsKeyDown(KeyboardKey.D) || Raylib.IsKeyDown(KeyboardKey.Right)) dir += 1;
            p.Velocity = p.Velocity with { X = dir * Player.RunSpeed };
        }
    }
    public void Update(Player p, float dt, Scene scene)
    {
        _elapsed += dt;
        if (!_hit && _elapsed >= 0.05f)
        {
            p.DealNailDamage(scene);
            _hit = true;
        }
        if (_inAir) p.ApplyGravity(dt);
        p.ApplyMovement(dt, scene);
        if (_elapsed >= Player.AttackDuration)
        {
            p.ChangeState(p.IsGrounded ? new IdleState() : new JumpState(midAir: true));
        }
    }
    public void Exit(Player p) { }
}

// ---------- Hurt ----------
public sealed class HurtState : IPlayerState
{
    public string Name => "Hurt";
    private float _elapsed;
    public void Enter(Player p) { _elapsed = 0; p.IsInvincible = true; }
    public void HandleInput(Player p) { /* нокдаун, ввод залочен */ }
    public void Update(Player p, float dt, Scene scene)
    {
        _elapsed += dt;
        p.ApplyGravity(dt); p.ApplyMovement(dt, scene);
        if (_elapsed >= Player.HurtDuration)
        {
            p.IsInvincible = false;
            p.ChangeState(p.IsGrounded ? new IdleState() : new JumpState(midAir: true));
        }
    }
    public void Exit(Player p) { p.IsInvincible = false; }
}

// ---------- Dead ----------
public sealed class DeadState : IPlayerState
{
    public string Name => "Dead";
    public void Enter(Player p) { p.Velocity = System.Numerics.Vector2.Zero; HollowDemo.Events.GameEvents.RaisePlayerDied(); }
    public void HandleInput(Player p) { }
    public void Update(Player p, float dt, Scene scene) { }
    public void Exit(Player p) { }
}
