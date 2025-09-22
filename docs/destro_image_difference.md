```mermaid
flowchart TD
    A[DISTRO_FEATURES] -->|Affects build & capabilities| B[Recipe build options<br/>(PACKAGECONFIG, dependencies)]
    A --> C[Available system subsystems<br/>(systemd, x11, wayland, alsa, wifi, etc.)]

    D[IMAGE_FEATURES] -->|Affects final rootfs| E[Installed package sets<br/>(ssh-server, package-management, tools-sdk, debug-tweaks)]
    D --> F[Rootfs assembly step<br/>(adds/removes pkgs after build)]

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

    %% Apply Material theme colors using valid Mermaid syntax
    class A distroStyle
    class D imageStyle

    classDef distroStyle fill:#1976d2,stroke:#1565c0,stroke-width:2px,color:#fff;
    classDef imageStyle fill:#e91e63,stroke:#ad1457,stroke-width:2px,color:#fff;
```
