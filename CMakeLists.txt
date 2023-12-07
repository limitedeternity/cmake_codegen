project(cmake_codegen CXX)

# ...
# ...
# ...

add_custom_target(Codegen ALL
    WORKING_DIRECTORY ${CMAKE_SOURCE_DIR}
    COMMAND pipenv sync --dev
    COMMAND pipenv run python -m _codegen generate

    BYPRODUCTS
    # ...
)

add_subdirectory(Project)
