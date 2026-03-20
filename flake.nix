{
  description = "C++ Development Environment";

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
          # Компиляторы и сборка
          gcc
          gnumake
          cmake

          # Отладка и анализ
          gdb
          valgrind

          # Интеграция с редактором (LSP)
          clang-tools # включает clangd
        ];

        shellHook = ''
          echo "🛠️ C/C++ Environment Loaded"
        '';
      };
    };
}
