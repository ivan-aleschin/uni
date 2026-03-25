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
              python3
              uv
              # --- Declarative ---
              erlang
              swi-prolog
              # --- SystemVerilog / FPGA ---
              iverilog      # iverilog: запуск testbench с initial/delays/$display
              verilator    # для лаб с import pkg::* (лаба 2+)
              gtkwave      # просмотр .vcd временных диаграмм
            ];
            shellHook = ''
              echo "🛠️ Uni Environment Loaded (C/C++, C#, Python, Qt6, SystemVerilog) [${system}]"
            '';
          };
        }
      );
    };
}
