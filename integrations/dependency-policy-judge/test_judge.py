# SPDX-License-Identifier: MIT

from judge import DependencyPolicyJudge


def test_accepts_pinned_package_json_dependency():
    judge = DependencyPolicyJudge()
    passed, reasons = judge.judge(
        {
            "files": {
                "package.json": '{"dependencies": {"left-pad": "1.3.0"}}',
            }
        }
    )

    assert passed is True
    assert reasons == []


def test_rejects_npm_install_lifecycle_script():
    judge = DependencyPolicyJudge()
    passed, reasons = judge.judge(
        {
            "files": {
                "package.json": '{"scripts": {"postinstall": "node ./install.js"}}',
            }
        }
    )

    assert passed is False
    assert "postinstall" in reasons[0]


def test_rejects_floating_npm_ranges_and_url_specs():
    judge = DependencyPolicyJudge()
    passed, reasons = judge.judge(
        {
            "files": {
                "package.json": (
                    '{"dependencies": {"a": "^1.2.3", "b": "latest", '
                    '"c": "git+https://example.invalid/repo.git"}}'
                ),
            }
        }
    )

    assert passed is False
    assert len(reasons) == 3
    assert any("range dependency" in reason for reason in reasons)
    assert any("floating dependency" in reason for reason in reasons)
    assert any("URL/VCS/local dependency" in reason for reason in reasons)


def test_rejects_unpinned_requirements():
    judge = DependencyPolicyJudge()
    passed, reasons = judge.judge(
        {
            "files": {
                "requirements.txt": "requests>=2.32\npytest==8.3.4\n",
            }
        }
    )

    assert passed is False
    assert reasons == ["requirements.txt:1: requirement uses range dependency: 'requests>=2.32'"]


def test_rejects_requirement_wildcards_mixed_constraints_and_direct_refs():
    judge = DependencyPolicyJudge()
    passed, reasons = judge.judge(
        {
            "files": {
                "requirements.txt": (
                    "pkg==*\n"
                    "pkg-two==1.*\n"
                    "pkg-three==1.0,>=1\n"
                    "local-lib @ ./local ==1.0\n"
                    "safe==1.2.3\n"
                )
            }
        }
    )

    assert passed is False
    assert len(reasons) == 4
    assert any("pkg==*" in reason and "wildcard dependency" in reason for reason in reasons)
    assert any("pkg-two==1.*" in reason and "wildcard dependency" in reason for reason in reasons)
    assert any("pkg-three==1.0,>=1" in reason and "mixed or broad dependency" in reason for reason in reasons)
    assert any("local-lib @ ./local ==1.0" in reason and "URL/VCS/local dependency" in reason for reason in reasons)


def test_rejects_python_alt_package_source_and_vcs():
    judge = DependencyPolicyJudge()
    passed, reasons = judge.judge(
        {
            "files": {
                "requirements-dev.txt": (
                    "--extra-index-url https://packages.example.invalid/simple\n"
                    "git+https://example.invalid/project.git\n"
                )
            }
        }
    )

    assert passed is False
    assert len(reasons) == 2
    assert "alternate package sources" in reasons[0]
    assert "URL/VCS/local dependency" in reasons[1]


def test_pyproject_dependencies_follow_same_pinning_policy():
    judge = DependencyPolicyJudge()
    passed, reasons = judge.judge(
        {
            "files": {
                "pyproject.toml": (
                    "[project]\n"
                    'dependencies = ["requests==2.32.3", "click>=8"]\n'
                    "[project.optional-dependencies]\n"
                    'dev = ["pytest==8.3.4", "ruff"]\n'
                )
            }
        }
    )

    assert passed is False
    assert any("click>=8" in reason for reason in reasons)
    assert any("'ruff'" in reason for reason in reasons)


def test_rejects_direct_reference_even_with_equals_marker():
    judge = DependencyPolicyJudge()
    passed, reasons = judge.judge(
        {
            "files": {
                "pyproject.toml": (
                    "[project]\n"
                    'dependencies = ["local-lib @ ./local ==1.0", "safe==1.0.0"]\n'
                )
            }
        }
    )

    assert passed is False
    assert reasons == [
        "pyproject.toml: project dependency uses URL/VCS/local dependency: 'local-lib @ ./local ==1.0'"
    ]


def test_pyproject_rejects_wildcard_and_mixed_specifiers():
    judge = DependencyPolicyJudge()
    passed, reasons = judge.judge(
        {
            "files": {
                "pyproject.toml": (
                    "[project]\n"
                    'dependencies = ["pkg==1.*", "pkg-two==1.0,>=1", "safe==1.0.0"]\n'
                )
            }
        }
    )

    assert passed is False
    assert len(reasons) == 2
    assert any("pkg==1.*" in reason and "wildcard dependency" in reason for reason in reasons)
    assert any("pkg-two==1.0,>=1" in reason and "mixed or broad dependency" in reason for reason in reasons)


def test_pyproject_poetry_and_pdm_sections_are_checked():
    judge = DependencyPolicyJudge()
    passed, reasons = judge.judge(
        {
            "files": {
                "pyproject.toml": (
                    "[tool.poetry.dependencies]\n"
                    'requests = "^2.32.0"\n'
                    'local-lib = { path = "../local-lib" }\n'
                    "[tool.pdm.dev-dependencies]\n"
                    'test = ["pytest>=8", "coverage==7.6.1"]\n'
                )
            }
        }
    )

    assert passed is False
    assert any("tool.poetry.dependencies" in reason and "requests^2.32.0" in reason for reason in reasons)
    assert any("tool.poetry.dependencies" in reason and "local-lib" in reason for reason in reasons)
    assert any("tool.pdm.dev-dependencies" in reason and "pytest>=8" in reason for reason in reasons)


def test_pyproject_uv_sections_are_checked():
    judge = DependencyPolicyJudge()
    passed, reasons = judge.judge(
        {
            "files": {
                "pyproject.toml": (
                    "[tool.uv]\n"
                    'dev-dependencies = ["ruff==0.8.0", "mypy>=1.10"]\n'
                )
            }
        }
    )

    assert passed is False
    assert reasons == [
        "pyproject.toml: tool.uv.dev-dependencies dependency uses range dependency: 'mypy>=1.10'"
    ]


def test_rejects_request_without_supported_manifests():
    judge = DependencyPolicyJudge()
    passed, reasons = judge.judge({"files": {"main.py": "print('ok')"}})

    assert passed is False
    assert reasons == ["no supported dependency manifests provided"]


def test_signs_and_verifies_verdict_envelope():
    judge = DependencyPolicyJudge()
    request = {"files": {"package.json": '{"dependencies": {"left-pad": "1.3.0"}}'}}

    envelope = judge.sign_verdict(request, issued_at=123)

    assert envelope["payload"]["passed"] is True
    assert envelope["payload"]["issued_at"] == 123
    assert envelope["signature_algorithm"] == "Ed25519"
    assert DependencyPolicyJudge.verify(envelope) is True


def test_verify_rejects_tampered_payload():
    judge = DependencyPolicyJudge()
    envelope = judge.sign_verdict(
        {"files": {"requirements.txt": "pytest==8.3.4\n"}},
        issued_at=123,
    )

    envelope["payload"]["passed"] = not envelope["payload"]["passed"]

    assert DependencyPolicyJudge.verify(envelope) is False
