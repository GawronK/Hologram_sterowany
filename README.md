# Interaktywny Hologram 3D z Raspberry Pi

## Opis
Projekt interaktywnego wyświetlacza holograficznego oparty na Raspberry Pi 4, kamerze Pi i piramidzie z plexi. Model STL (np. kaczka) jest sterowany ruchem dłoni wykrywanym przez kamerę i bibliotekę MediaPipe.

## Status projektu
W fazie projektowania (hardware), funkcjonalny kod do poruszania modelem STL na podstawie ruchu dłoni.

## Funkcje
- [x] Detekcja dłoni (MediaPipe)
- [x] Sterowanie modelem STL (obrót i skalowanie)
- [ ] Integracja z kamerą Pi (testowane na PC)
- [ ] Obudowa z plexi (ostrosłup)
- [ ] Finalna wersja na Raspberry Pi 4

## Wymagania
- Python 3.7+
- Raspberry Pi 4 (docelowo)
- Kamera (USB lub Pi Camera)
- Biblioteki:
  - `opencv-python`
  - `mediapipe`
  - `vtk`
  - `numpy`

## Instalacja zależności
```bash
pip install opencv-python mediapipe vtk numpy
```