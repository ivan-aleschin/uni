{
  description = "University Projects Environment (C++, C#, Python)";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
  };

  outputs = { self, nixpkgs }:
    let
      # Поддерживаемые архитектуры и ОС (Linux и macOS на Intel и Apple Silicon)
      supportedSystems = [ "x86_64-linux" "aarch64-linux" "x86_64-darwin" "aarch64-darwin" ];

      # Вспомогательная функция для генерации конфигурации под каждую ОС
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
            ] ++ lib.optionals stdenv.isLinux [
              # gdb и valgrind плохо или совсем не работают на современных macOS,
              # поэтому устанавливаем их только на Linux
              gdb
              valgrind
            ] ++ [
              # --- C# ---
              dotnet-sdk

              # --- Python ---
              python3
              uv
            ];

            shellHook = ''
              echo "🛠️ Uni Environment Loaded (C/C++, C#, Python) [${system}]"
            '';
          };
        }
      );
    };
}
