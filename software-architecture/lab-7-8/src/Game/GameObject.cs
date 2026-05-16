using System.Numerics;
using Raylib_cs;

namespace HollowDemo.Game;

/// <summary>
/// Composite — общий тип всех объектов сцены: игрок, враги, платформы,
/// души, снаряды. Клиент (Scene) хранит коллекцию GameObject и единообразно
/// вызывает Update / Draw, не зная конкретного типа.
/// </summary>
public abstract class GameObject
{
    public Vector2 Position;
    public Vector2 Size;
    public bool IsAlive { get; protected set; } = true;

    protected GameObject(Vector2 position, Vector2 size)
    {
        Position = position;
        Size = size;
    }

    public Rectangle Bounds => new(Position.X, Position.Y, Size.X, Size.Y);

    public abstract void Update(float dt, Scene scene);
    public abstract void Draw();

    public virtual void OnCollide(GameObject other) { }

    public void Kill() => IsAlive = false;
}
