namespace HollowDemo.Events;

/// <summary>
/// Subject паттерна Observer. Конкретные значения событий передаются
/// через payload-структуры. Подписчики (HUD, GameOverScreen,
/// ScoreCounter, …) присоединяются через += и отписываются через -=.
///
/// Это не глобальное состояние — это шина событий, которую сцена
/// прокидывает в свои объекты. Сделана статической ради простоты:
/// в реальной игре сюда бы передавался экземпляр через DI.
/// </summary>
public static class GameEvents
{
    public static event Action<int, int>? PlayerHpChanged; // current, max
    public static event Action<int, int>? PlayerSoulChanged; // current, max
    public static event Action<int>? PlayerScoredKill; // +killCount
    public static event Action? PlayerDied;
    public static event Action<int>? EnemyDied; // id

    public static void RaisePlayerHpChanged(int current, int max)
        => PlayerHpChanged?.Invoke(current, max);

    public static void RaisePlayerSoulChanged(int current, int max)
        => PlayerSoulChanged?.Invoke(current, max);

    public static void RaisePlayerScoredKill(int killCount)
        => PlayerScoredKill?.Invoke(killCount);

    public static void RaisePlayerDied() => PlayerDied?.Invoke();

    public static void RaiseEnemyDied(int id) => EnemyDied?.Invoke(id);

    /// <summary>
    /// Снятие всех подписчиков при перезапуске игры — иначе остаются
    /// «висящие» подписки на старые HUD-объекты.
    /// </summary>
    public static void ClearAllSubscribers()
    {
        PlayerHpChanged = null;
        PlayerSoulChanged = null;
        PlayerScoredKill = null;
        PlayerDied = null;
        EnemyDied = null;
    }
}
