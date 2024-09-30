project(cmake_codegen LANGUAGES CXX VERSION "1.0.0")

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

block()
    add_subdirectory(Project)
endblock()
