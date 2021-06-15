@echo off
rmdir /s /q %1
c:
cd %2
rmdir /s /q "Anaconda3 (64-bit)"
