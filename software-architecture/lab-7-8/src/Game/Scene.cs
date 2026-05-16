using Raylib_cs;

namespace HollowDemo.Game;

/// <summary>
/// Composite (составной объект) и одновременно «клиент» паттерна Composite.
/// Хранит коллекцию GameObject, единообразно их обновляет и рисует.
/// Через сцену объекты находят друг друга для проверки коллизий —
/// игрок не «знает» о врагах напрямую, он спрашивает сцену.
/// </summary>
public sealed class Scene
{
    private readonly List<GameObject> _objects = new();
    private readonly List<GameObject> _pending = new();
    public Player.Player? Player { get; set; }

    // Координата Y, ниже которой игрок (и враги) считаются упавшими «за карту».
    // Конфигурируется при сборке уровня в Program.cs.
    public float DeathY { get; set; } = 2000f;
    // Границы уровня — нужны камере для clamp'а.
    public Rectangle WorldBounds { get; set; }

    public IReadOnlyList<GameObject> Objects => _objects;

    public void Add(GameObject obj) => _pending.Add(obj);

    public void Update(float dt)
    {
        // Внесение отложенных добавлений (Factory во время Update'а
        // спавнит врагов/снаряды — это безопасно).
        if (_pending.Count > 0)
        {
            _objects.AddRange(_pending);
            _pending.Clear();
        }
        foreach (var obj in _objects)
        {
            if (obj.IsAlive) obj.Update(dt, this);
        }
        _objects.RemoveAll(o => !o.IsAlive);
    }

    public void Draw()
    {
        foreach (var obj in _objects)
        {
            if (obj.IsAlive) obj.Draw();
        }
    }

    public IEnumerable<T> ObjectsOf<T>() where T : GameObject =>
        _objects.OfType<T>().Where(o => o.IsAlive);
}
