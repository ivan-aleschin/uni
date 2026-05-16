using HollowDemo.Game;

namespace HollowDemo.Player;

/// <summary>
/// Абстрактное состояние игрока (State pattern). Каждое конкретное
/// состояние знает, как обрабатывать ввод, обновлять физику и
/// переходить в другое состояние.
/// </summary>
public interface IPlayerState
{
    string Name { get; }
    void Enter(Player player);
    void HandleInput(Player player);
    void Update(Player player, float dt, Scene scene);
    void Exit(Player player);
}
