using HollowDemo.Game;

namespace HollowDemo.Enemies;

/// <summary>
/// Strategy — поведение врага (как он перемещается и нападает).
/// Каждый конкретный тип врага получает свою стратегию в конструкторе.
/// Позволяет один и тот же класс Enemy комбинировать с разным AI.
/// </summary>
public interface IEnemyStrategy
{
    string Name { get; }
    void Update(Enemy enemy, Player.Player player, Scene scene, float dt);
}
