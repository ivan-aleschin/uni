using HollowDemo.Events;
using Raylib_cs;

namespace HollowDemo.UI;

/// <summary>
/// ConcreteObserver — слушает только событие PlayerDied. Когда оно
/// приходит, поднимает флаг и Program переключает игру в overlay-режим
/// с подсказкой «R — restart».
/// </summary>
public sealed class GameOverScreen : IDisposable
{
    public static Font Font;
    public bool IsActive { get; private set; }

    public GameOverScreen()
    {
        GameEvents.PlayerDied += OnDied;
    }

    private void OnDied() => IsActive = true;

    public void Draw()
    {
        if (!IsActive) return;
        Raylib.DrawRectangle(0, 0, Raylib.GetScreenWidth(), Raylib.GetScreenHeight(),
            new Color(0, 0, 0, 180));
        const string title = "ВЫ ПАЛИ";
        const string hint = "R — рестарт   Esc — выход";
        var tSz = Raylib.MeasureTextEx(Font, title, 56, 0);
        var hSz = Raylib.MeasureTextEx(Font, hint, 22, 0);
        Raylib.DrawTextEx(Font, title,
            new System.Numerics.Vector2((Raylib.GetScreenWidth() - tSz.X) / 2,
                                        Raylib.GetScreenHeight() / 2 - 60),
            56, 0, new Color(220, 60, 60, 255));
        Raylib.DrawTextEx(Font, hint,
            new System.Numerics.Vector2((Raylib.GetScreenWidth() - hSz.X) / 2,
                                        Raylib.GetScreenHeight() / 2 + 10),
            22, 0, Color.White);
    }

    public void Dispose() { GameEvents.PlayerDied -= OnDied; }
}
