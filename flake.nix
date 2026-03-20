{
  description = "University Projects Environment (C++, C#, Python)";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
  };

  outputs = { self, nixpkgs }:
    let
      system = "x86_64-linux";
      pkgs = nixpkgs.legacyPackages.${system};
    in
    {
      devShells.${system}.default = pkgs.mkShell {
        packages = with pkgs; [
          # --- C/C++ ---
          gcc
          gnumake
          cmake
          gdb
          valgrind
          clang-tools

          # --- C# ---
          dotnet-sdk

          # --- Python ---
          # Ответ на твой вопрос:
          # Сам Python и утилиту `uv` мы ставим глобально для проекта через flake.nix.
          # А вот конкретные зависимости (библиотеки) для каждой отдельной лабы
          # стоит контролировать исключительно через `uv` и `pyproject.toml` (или `uv.lock`).
          # `uv` будет создавать локальные `.venv` папки, и это самый правильный, быстрый и современный подход!
          python3
          uv
        ];

        shellHook = ''
          echo "🛠️ Uni Environment Loaded (C/C++, C#, Python)"
        '';
      };
    };
}
