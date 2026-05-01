{
  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-25.11";
    flake-utils.url = "github:numtide/flake-utils";
    hermes_84.url = "github:Sighery/hermes_84-nix";
  };

  outputs = { self, nixpkgs, flake-utils, hermes_84 }:
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
            hermes_84.packages.${system}.default
          ];
          shellHook = ''
            export SHELL=/run/current-system/sw/bin/bash
          '';
        };
      }
    );
}
