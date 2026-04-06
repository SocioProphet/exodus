---
name: Repo bootstrap
description: Bootstrap work item for the Exodus repository
title: "[bootstrap] "
labels: [bootstrap]
body:
  - type: textarea
    id: scope
    attributes:
      label: Scope
      description: What should be created or changed?
    validations:
      required: true
  - type: textarea
    id: acceptance
    attributes:
      label: Acceptance criteria
      description: How will we know the work is done?
    validations:
      required: true
