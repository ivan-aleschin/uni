using System.Numerics;
using HollowDemo.Game;
using Raylib_cs;

namespace HollowDemo.Enemies;

/// <summary>
/// Factory Method: вместо new HuskEnemy(...) / new FlyEnemy(...) в клиенте
/// — единая точка создания, склеивающая правильную текстуру, размер,
/// HP, урон и стратегию для каждого вида врага. Клиент (Program/Scene)
/// знает только enum EnemyKind.
/// </summary>
public static class EnemyFactory
{
    public enum EnemyKind { Husk, Fly, Archer }

    public static Texture2D TexHusk, TexFly, TexArcher;

    public static Enemy Spawn(EnemyKind kind, Vector2 position) => kind switch
    {
        // Husk — низкий силуэт ~20×16 px у нижнего края 32×32 спрайта.
        EnemyKind.Husk => new Enemy(
            kind: "Husk",
            spawn: position,
            size: new Vector2(32, 32),
            tex: TexHusk,
            strategy: new PatrolStrategy(),
            hp: 2,
            damage: 1,
            useGravity: true,
            hitBoxSize: new Vector2(20, 16),
            hitBoxOffset: new Vector2(6, 14)),

        // Fly — круглое существо ~18×18 px по центру 32×32.
        EnemyKind.Fly => new Enemy(
            kind: "Fly",
            spawn: position,
            size: new Vector2(32, 32),
            tex: TexFly,
            strategy: new ChaseStrategy(),
            hp: 1,
            damage: 1,
            useGravity: false,
            hitBoxSize: new Vector2(18, 18),
            hitBoxOffset: new Vector2(7, 7)),

        // Archer — вертикальный силуэт ~16×24 px.
        EnemyKind.Archer => new Enemy(
            kind: "Archer",
            spawn: position,
            size: new Vector2(32, 32),
            tex: TexArcher,
            strategy: new RangedStrategy(),
            hp: 3,
            damage: 1,
            useGravity: true,
            hitBoxSize: new Vector2(16, 24),
            hitBoxOffset: new Vector2(8, 8)),

        _ => throw new ArgumentOutOfRangeException(nameof(kind))
    };
}
