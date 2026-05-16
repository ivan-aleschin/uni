using System.Numerics;
using HollowDemo.Game;
using Raylib_cs;

namespace HollowDemo.Enemies;

/// <summary>
/// Снаряд, выпускаемый стрелком. Лист композиции: летит по прямой,
/// исчезает при контакте с платформой / игроком или после таймаута.
/// </summary>
public sealed class Projectile : GameObject
{
    public static Texture2D Texture;
    private readonly Vector2 _velocity;
    private float _life = 3f;

    public Projectile(Vector2 position, Vector2 velocity)
        : base(position, new Vector2(8, 8))
    {
        _velocity = velocity;
    }

    public override void Update(float dt, Scene scene)
    {
        _life -= dt;
        Position += _velocity * dt;
        if (_life <= 0) { Kill(); return; }

        foreach (var plat in scene.ObjectsOf<Platform>())
        {
            if (Raylib.CheckCollisionRecs(Bounds, plat.Bounds)) { Kill(); return; }
        }
        if (scene.Player is { } p && Raylib.CheckCollisionRecs(Bounds, p.HitBox))
        {
            p.TakeHit(Position); Kill();
        }
    }

    public override void Draw()
    {
        Raylib.DrawTextureV(Texture, Position, Color.White);
    }
}
