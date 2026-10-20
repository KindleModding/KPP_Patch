{
  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
    hermes_84.url = "github:Sighery/hermes_84-nix";
  };

  outputs = { self, nixpkgs, hermes_84 }: let
    forAllSystems = function:
      nixpkgs.lib.genAttrs nixpkgs.lib.systems.flakeExposed function;
  in {
    devShells = forAllSystems (system:
    let
      pkgs = import nixpkgs { inherit system; };
    in {
      default = pkgs.mkShell {
        buildInputs = with pkgs; [ bashInteractive ];

        packages = with pkgs; [
          python314
          python314Packages.pip
          python314Packages.virtualenv
          python314Packages.ipython
          coreutils
          bashInteractive
          xxd
          hermes_84.packages.${system}.default
        ];

        shellHook = ''
          export SHELL=/run/current-system/sw/bin/bash
        '';
      };
    });
  };
}
