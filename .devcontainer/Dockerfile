FROM koxudaxi/python:3.14-rc-bullseye

# # Allow PYO3 to build even though the configured interpreter version (3.14)
# # is greater than PYO3's stated limit (3.12)
# ENV PYO3_USE_ABI3_FORWARD_COMPATIBILITY=1

# Tell pip not to worry about the user environment
ENV PIP_ROOT_USER_ACTION=ignore

# Various things to make devcontainers run smoothly
ENV EDITOR="code --wait"

# # Install locales and locales-all, required to build sphinx docs
# # in the devcontainer, since sphinx main starts sith `locale.setlocale(LC_ALL, '')`
# #
# # Also, install jq (required for building the playground)
# RUN apt-get update && apt-get install -y locales locales-all jq

# # Install rust and cargo to support watchfiles, rpds-py, and metadata
# RUN curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y
