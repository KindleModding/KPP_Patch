{
  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-25.11";
    flake-utils.url = "github:numtide/flake-utils";
  };

  outputs = { self, nixpkgs, flake-utils }:
    flake-utils.lib.eachDefaultSystem (system:
      let
        pkgs = import nixpkgs {
          inherit system;
        };
      in {
        devShells.default = pkgs.mkShell {
          buildInputs = with pkgs; [ bashInteractive ];
          packages = with pkgs; [
            python3
            python313Packages.pip
            python313Packages.virtualenv
            python313Packages.ipython
            python313Packages.pytest
            python313Packages.black
            coreutils
            bashInteractive
            xxd
          ];
          shellHook = ''
            export SHELL=/run/current-system/sw/bin/bash
          '';
        };
      }
    );
}
