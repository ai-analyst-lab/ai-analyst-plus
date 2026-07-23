"""Deterministic runtime helpers for Codex skill smoke tests.

These helpers implement small, testable slices of migrated skill behavior so
local E2E tests can validate outcomes without invoking an LLM or external
services. They are intentionally conservative and fixture-friendly.
"""
