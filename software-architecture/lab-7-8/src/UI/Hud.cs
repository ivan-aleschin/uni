using HollowDemo.Events;
using Raylib_cs;

namespace HollowDemo.UI;

/// <summary>
/// ConcreteObserver — рисует полоску HP, полоску души и счётчик убитых.
/// Подписывается на события игры через GameEvents.* и хранит у себя
/// последнее известное состояние (pull-модель нам не нужна).
/// </summary>
public sealed class Hud : IDisposable
{
    public static Font Font;
    private int _hp, _hpMax = 1;
    private int _soul, _soulMax = 1;
    private int _kills;

    public Hud()
    {
        GameEvents.PlayerHpChanged += OnHp;
        GameEvents.PlayerSoulChanged += OnSoul;
        GameEvents.PlayerScoredKill += OnKill;
    }

    private void OnHp(int cur, int max) { _hp = cur; _hpMax = max; }
    private void OnSoul(int cur, int max) { _soul = cur; _soulMax = max; }
    private void OnKill(int total) => _kills = total;

    public void Draw()
    {
        // HP — пять «масок» в ряд.
        int x0 = 18, y0 = 18;
        for (int i = 0; i < _hpMax; i++)
        {
            var col = i < _hp ? new Color(232, 232, 236, 255) : new Color(60, 60, 70, 255);
            Raylib.DrawRectangle(x0 + i * 22, y0, 18, 18, col);
            Raylib.DrawRectangleLines(x0 + i * 22, y0, 18, 18, Color.Black);
        }
        // Soul — синяя полоска под HP.
        int barW = (_hpMax * 22) - 4;
        Raylib.DrawRectangle(x0, y0 + 26, barW, 8, new Color(30, 30, 60, 255));
        Raylib.DrawRectangle(x0, y0 + 26, (int)(barW * (_soul / (float)_soulMax)), 8,
            new Color(160, 220, 255, 255));
        Raylib.DrawRectangleLines(x0, y0 + 26, barW, 8, Color.Black);
        Raylib.DrawTextEx(Font, $"Душа {_soul}/{_soulMax}",
            new System.Numerics.Vector2(x0, y0 + 40), 18, 0, Color.White);
        // Счётчик убитых.
        string kills = $"Убито: {_kills}";
        var sz = Raylib.MeasureTextEx(Font, kills, 22, 0);
        Raylib.DrawTextEx(Font, kills,
            new System.Numerics.Vector2(Raylib.GetScreenWidth() - sz.X - 18, y0),
            22, 0, Color.White);
    }

    public void Dispose()
    {
        GameEvents.PlayerHpChanged -= OnHp;
        GameEvents.PlayerSoulChanged -= OnSoul;
        GameEvents.PlayerScoredKill -= OnKill;
    }
}
