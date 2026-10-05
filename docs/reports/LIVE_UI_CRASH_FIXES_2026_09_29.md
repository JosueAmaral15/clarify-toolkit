# Live UI Crash Repairs - 2026-09-29

Status: scoped local repair validated, not committed. Continued on 2026-10-04
for Portuguese and revalidated on 2026-10-05. Preserve the separate unfinished
Explorer Qt patch and unrelated `example.py`; no push or promotion.

## Bounded Plan

1. Repair the assistant's nonexistent settings calls using the existing get/set
   API, and verify entry points/feedback with isolated settings and fake services.
2. Repair plugin toggles through shared loader lifecycle APIs, including failure
   state; fix History lazy creation and layout without full MainWindow startup.
3. Normalize mixed flat/nested translation catalogues and load English fallback;
   refresh affected menus/dialogs/tabs without losing content, selection or state.
   Audit residual untranslated strings; do not claim complete localization.
4. Validate serial lightweight Qt modules with RAM85%/treeRSS600MiB/wall180s and
   pytest20s including fixtures. No providers, real documents or full GUI startup.
5. Separate Python exceptions, the user's native signal11, AT-SPI/QTextCursor
   warnings and the external Xed/PyGObject errors. Do not disable accessibility,
   upgrade dependencies, delete user settings or change OS packages speculatively.

## Findings And Repair

- The 08:23/08:24 reports confirm Assistant's missing `SettingsManager.get_value`
  and the Plugins menu's missing `MainWindow._toggle_plugin`. Their source
  snippets do not match the current code at the reported lines; an older running
  process is a possibility, not a proven explanation.
- The actual desktop core for Clarify PID 431630 is present in systemd-coredump
  (signal11, 2026-09-29 08:26:05 local). A read-only bounded GDB backtrace
  reaches `QApplicationPrivate::notify_helper`, `QBoxLayout::takeAt`,
  `QLayout::~QLayout` and Python `HistoryDock._create_layout` / `_setup_ui`.
  `BaseDock` had already installed a layout; `HistoryDock` installed a second
  one. It now adds its widgets to the existing owned layout. This is strong
  evidence for the reported History-related desktop crash, not proof that all
  other historical Qt faults are solved. No core payload or user document was
  copied into the repository.
- Assistant and Tutorials entry points now use existing settings `get`/`set`.
  The nonmodal dialog reuses its instance; fake-provider requests run in a
  registered parentless thread, reject duplicates, defer closure until the
  worker finishes and avoid callbacks to a deleted parent. Interruption is
  advisory and cannot forcibly cancel a blocked provider call.
- Plugin menu and dialog use one loader transition that reverts preference
  state on activation/deactivation failure. Rebuilding menus for language
  changes disposes old owned actions/shortcuts while retaining plugin-added
  entries, submenu state and foreign roots. PluginBase now looks up translated
  top-level menus by stable key, so `Tools/My Plugin` reuses the Portuguese
  `Ferramentas` root. The resumed test exposed that a root queued for deferred
  deletion could still match as a QObject child. Lookup now requires the menu's
  own action to remain installed in the current parent, excluding stale roots.
- The translator now reads nested and dotted keys and loads English fallback
  before the current language. Saved language applies before UI construction.
  Portuguese was confirmed by the user: affected menus, tabs, Assistant,
  Plugins, History details and Tutorials navigation/welcome/search now refresh
  without replacing the current selection or document content. Built-in
  tutorial Markdown/FAQ and other legacy tools are not fully translated.

## Validation And Barrier

91 distinct focused tests passed across isolated serial modules before the
final PluginBase change. These include 20 History creation/deletion cycles
with forced GC, plugin failure rollback and menu extension preservation,
assistant request/close/parent-deletion, locale catalogues, Portuguese
Tutorials state, plugin consumers and 11 Qt completion lifecycle cases.
System RAM85%, treeRSS600MiB, wall180s and pytest20s (including fixtures)
were enforced with temporary HOME/settings/logs and offscreen Qt. Largest
passing test process peaked at about206MiB tree RSS; no provider or full
MainWindow startup ran. Pylint-E for 11 production modules, AST for 15 Python
files, seven JSON parses and `git diff --check` passed before the final
PluginBase edit. These are focused checks, not full-suite or live-desktop proof.

The new plugin API integration test was initially stopped by the RAM85% guard
before collection: exit125, peak treeRSS60.1MiB, no native crash. No retry was
made in that session. On 2026-10-05, with about1GiB physical RAM available and
8GiB swap configured, the same physical-RAM and process guards remained active.
The first resumed module run reached the new test and reported a deterministic
duplicate-root assertion after15 passes, exit1 and peak181.2MiB; this was not a
native crash or resource abort. After filtering deferred stale menus, the
current state passed these isolated serial modules:

- `test_live_ui_actions.py`:17 passed, peak200.3MiB;
- `test_plugin_system.py`:16 passed, peak74.0MiB;
- `test_tutorials_localization.py`:3 passed, peak195.1MiB;
- translation catalogue lookup:10 passed;
- i18n expansion:14 passed;
- diagnostic probe guards and command construction:47 passed.

That is60 directly affected functional tests plus47 probe tests in the resumed
validation. No guard fired and no native crash occurred. Pylint error checks for
13 production/diagnostic files, AST parsing for19 Python files, seven JSON
catalogues and `git diff --check` passed. A repository-style Black check is not
clean:14 accumulated modified files would be reformatted, so no broad mechanical
rewrite was applied. These results validate the scoped repair, not the full GUI,
providers or desktop lifecycle. No commit or push followed.

The `t.accessibility.atspi` warning has no matching crash backtrace here.
`QTextCursor::setPosition` reported an out-of-range position but no caller
stack; its source remains undetermined. The Xed plugin loader warnings came
from a separate `xed` PID after opening logs. A read-only check found `gi`
under `/usr/bin/python3` (3.10), while Clarify's 3.12 virtualenv has no `gi`;
an inherited/interpreter mismatch is plausible, but not established. No
system package, accessibility setting, user config or document was modified.

## Remaining

1. Inspect Portuguese in a new desktop Clarify process; an already-running
   process has old code. This is a user-visible acceptance check, not a reason
   to run providers or load real documents during automated validation.
2. Continue LEG-10's app-wide Portuguese audit for older tool controls and
   bundled tutorial/FAQ content. Do not treat fallback English as translation.
3. Keep the historical Explorer FE05 native fault, MainWindow/theme issue,
   security and CI gates separate and open; this History core does not close them.
