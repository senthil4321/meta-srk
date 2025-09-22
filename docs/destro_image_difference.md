```mermaid
flowchart TD
    A[DISTRO_FEATURES] -->|Affects build & capabilities| B[Recipe build options<br>(PACKAGECONFIG, dependencies)]
    A --> C[Available system subsystems<br>(systemd, x11, wayland, alsa, wifi, etc.)]

    D[IMAGE_FEATURES] -->|Affects final rootfs| E[Installed package sets<br>(ssh-server, package-management, tools-sdk, debug-tweaks)]
    D --> F[Rootfs assembly step<br>(adds/removes pkgs after build)]

    subgraph Scope
        A
        D
    end

    subgraph Effects
        B
        C
        E
        F
    end

    A:::distroStyle
    D:::imageStyle

    classDef distroStyle fill=#4CAF50,stroke=#2E7D32,color=white
    classDef imageStyle fill=#2196F3,stroke=#0D47A1,color=white
