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

    class A distroStyle
    class D imageStyle

    classDef distroStyle fill=#2196f3,stroke=#1976d2,color=#fff; /* Material Blue */
    classDef imageStyle fill=#e91e63,stroke=#ad1457,color=#fff; /* Material Pink */
```
