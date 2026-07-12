@echo off
setlocal
cd /d "%~dp0"
echo ================= FULL GATE SUITE (all 3 repos) =================
echo.
echo ---- ds-demand-cockpit (10 gates, ~2-3 min) ----
pushd "ds-demand-cockpit\ds-demand-cockpit"
python tests\run_tests.py
popd
echo.
echo ---- ds-copilot (eval 25/25 expected) ----
pushd "ds-copilot\ds-copilot"
python tests\eval_harness.py
popd
echo.
echo ---- ds-doc-to-decision (decisions 40/40 + 13/13 expected) ----
pushd "ds-doc-to-decision\ds-doc-to-decision"
python tests\gate_no_peek.py
python tests\gate_m3.py
python tests\gate_m5_loop.py
popd
echo.
echo ================= SUITE DONE - scroll up for GREEN/RED =================
pause
