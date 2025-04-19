{
  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
    flake-utils.url = "github:numtide/flake-utils";
  };
  outputs = {
    self,
    nixpkgs,
    flake-utils,
  }:
    flake-utils.lib.eachDefaultSystem
    (
      system: let
        pkgs = import nixpkgs {
          inherit system;
          config.allowUnfree = true;
        };
      in
        with pkgs; {
          devShells = {
            default = mkShell.override {stdenv = clangStdenv;} {
              packages = [
                (python3.withPackages (ps:
                  with ps; [
                    pyside6
                    websockets
                    pyaudio
                  ]
                ))
                uv
                pyright

                # QT
                qt6.qtbase
                qt6.qtdeclarative
              ];

              shellHook = ''
                export QML_IMPORT_PATH="${pkgs.qt6.qtdeclarative}/lib/qt-6/qml"
              '';
            };
          };
        }
    );
}
