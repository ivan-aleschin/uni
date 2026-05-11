{
  description = "University Projects Environment (C++, C#, Python, Qt6)";
  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
  };
  outputs = { self, nixpkgs }:
    let
      supportedSystems = [ "x86_64-linux" "aarch64-linux" "x86_64-darwin" "aarch64-darwin" ];
      forAllSystems = nixpkgs.lib.genAttrs supportedSystems;
    in
    {
      devShells = forAllSystems (system:
        let
          pkgs = nixpkgs.legacyPackages.${system};
        in
        {
          default = pkgs.mkShell {
            packages = with pkgs; [
              # --- C/C++ ---
              gcc
              gnumake
              cmake
              clang-tools
              pkg-config
              # --- Qt6 для GUI ---
              qt6.qtbase
              qt6.qtwayland
              qt6.qtimageformats
              qt6.wrapQtAppsHook
            ] ++ pkgs.lib.optionals pkgs.stdenv.isLinux [
              gdb
              valgrind
            ] ++ [
              # --- C# ---
              dotnet-sdk
              # --- Python ---
              # python3.withPackages — единственный способ поставить C-расширения
              # (psycopg2, numpy и т.д.) на NixOS: pip/uv бинарные колёса не работают
              # из-за отсутствия стандартных /lib путей. Декларация зависимостей — в
              # databases/pgcli/pyproject.toml; Nix её воспроизводит через withPackages.
              (python3.withPackages (ps: with ps; [
                psycopg2   # PostgreSQL адаптер для лаб по БД
              ]))
              uv           # менеджер пакетов для чистых Python-проектов (без C-ext)
              # --- Declarative ---
              erlang
              swi-prolog
              # --- SystemVerilog / FPGA ---
              iverilog      # iverilog: запуск testbench с initial/delays/$display
              verilator    # для лаб с import pkg::* (лаба 2+)
              gtkwave      # просмотр .vcd временных диаграмм
              # --- LSP серверы для Neovim ---
              lua-language-server    # Lua (конфиг Neovim / скрипты)
              pyright                # Python (статический анализ + LSP)
              nil                    # Nix (*.nix файлы)
              sqls                   # SQL (PostgreSQL, MySQL и др.)
              omnisharp-roslyn       # C# (.NET)
              bash-language-server   # Bash / Shell-скрипты
              # clangd входит в clang-tools (уже выше)
            ];
            shellHook = ''
              echo "🛠️ Uni Environment Loaded (C/C++, C#, Python, Qt6, SystemVerilog) [${system}]"
            '';
          };
        }
      );
    };
}
