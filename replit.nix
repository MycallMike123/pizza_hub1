{ pkgs }: {
  deps = [
    pkgs.wget
    pkgs.python38
    pkgs.python38Packages.flask
    pkgs.python38Packages.sqlalchemy
    pkgs.python38Packages.gunicorn
  ];
}