from typing import cast, Sequence

from pytest import deprecated_call, raises  # type: ignore

from graphql_relay import (
    connection_from_array,
    connection_from_array_slice,
    cursor_for_object_in_connection,
    Connection,
    Edge,
    PageInfo,
)

# noinspection PyProtectedMember
from graphql_relay import connection_from_list, connection_from_list_slice


def describe_connection_from_array():
    letters = ["A", "B", "C", "D", "E"]

    def describe_basic_slicing():
        def returns_all_elements_without_filters():
            c = connection_from_array(letters, {})
            assert c == Connection(
                edges=[
                    Edge(node="A", cursor="YXJyYXljb25uZWN0aW9uOjA="),
                    Edge(node="B", cursor="YXJyYXljb25uZWN0aW9uOjE="),
                    Edge(node="C", cursor="YXJyYXljb25uZWN0aW9uOjI="),
                    Edge(node="D", cursor="YXJyYXljb25uZWN0aW9uOjM="),
                    Edge(node="E", cursor="YXJyYXljb25uZWN0aW9uOjQ="),
                ],
                pageInfo=PageInfo(
                    startCursor="YXJyYXljb25uZWN0aW9uOjA=",
                    endCursor="YXJyYXljb25uZWN0aW9uOjQ=",
                    hasPreviousPage=False,
                    hasNextPage=False,
                ),
            )

        def respects_a_smaller_first():
            c = connection_from_array(letters, dict(first=2))
            assert c == Connection(
                edges=[
                    Edge(node="A", cursor="YXJyYXljb25uZWN0aW9uOjA="),
                    Edge(node="B", cursor="YXJyYXljb25uZWN0aW9uOjE="),
                ],
                pageInfo=PageInfo(
                    startCursor="YXJyYXljb25uZWN0aW9uOjA=",
                    endCursor="YXJyYXljb25uZWN0aW9uOjE=",
                    hasPreviousPage=False,
                    hasNextPage=True,
                ),
            )

        def respects_an_overly_large_first():
            c = connection_from_array(letters, dict(first=10))
            assert c == Connection(
                edges=[
                    Edge(node="A", cursor="YXJyYXljb25uZWN0aW9uOjA="),
                    Edge(node="B", cursor="YXJyYXljb25uZWN0aW9uOjE="),
                    Edge(node="C", cursor="YXJyYXljb25uZWN0aW9uOjI="),
                    Edge(node="D", cursor="YXJyYXljb25uZWN0aW9uOjM="),
                    Edge(node="E", cursor="YXJyYXljb25uZWN0aW9uOjQ="),
                ],
                pageInfo=PageInfo(
                    startCursor="YXJyYXljb25uZWN0aW9uOjA=",
                    endCursor="YXJyYXljb25uZWN0aW9uOjQ=",
                    hasPreviousPage=False,
                    hasNextPage=False,
                ),
            )

        def respects_a_smaller_last():
            c = connection_from_array(letters, dict(last=2))
            assert c == Connection(
                edges=[
                    Edge(node="D", cursor="YXJyYXljb25uZWN0aW9uOjM="),
                    Edge(node="E", cursor="YXJyYXljb25uZWN0aW9uOjQ="),
                ],
                pageInfo=PageInfo(
                    startCursor="YXJyYXljb25uZWN0aW9uOjM=",
                    endCursor="YXJyYXljb25uZWN0aW9uOjQ=",
                    hasPreviousPage=True,
                    hasNextPage=False,
                ),
            )

        def respects_an_overly_large_last():
            c = connection_from_array(letters, dict(last=10))
            assert c == Connection(
                edges=[
                    Edge(node="A", cursor="YXJyYXljb25uZWN0aW9uOjA="),
                    Edge(node="B", cursor="YXJyYXljb25uZWN0aW9uOjE="),
                    Edge(node="C", cursor="YXJyYXljb25uZWN0aW9uOjI="),
                    Edge(node="D", cursor="YXJyYXljb25uZWN0aW9uOjM="),
                    Edge(node="E", cursor="YXJyYXljb25uZWN0aW9uOjQ="),
                ],
                pageInfo=PageInfo(
                    startCursor="YXJyYXljb25uZWN0aW9uOjA=",
                    endCursor="YXJyYXljb25uZWN0aW9uOjQ=",
                    hasPreviousPage=False,
                    hasNextPage=False,
                ),
            )

    def describe_pagination():
        def respects_first_and_after():
            c = connection_from_array(
                letters, dict(first=2, after="YXJyYXljb25uZWN0aW9uOjE=")
            )
            assert c == Connection(
                edges=[
                    Edge(node="C", cursor="YXJyYXljb25uZWN0aW9uOjI="),
                    Edge(node="D", cursor="YXJyYXljb25uZWN0aW9uOjM="),
                ],
                pageInfo=PageInfo(
                    startCursor="YXJyYXljb25uZWN0aW9uOjI=",
                    endCursor="YXJyYXljb25uZWN0aW9uOjM=",
                    hasPreviousPage=False,
                    hasNextPage=True,
                ),
            )

        def respects_first_and_after_with_long_first():
            c = connection_from_array(
                letters, dict(first=10, after="YXJyYXljb25uZWN0aW9uOjE=")
            )
            assert c == Connection(
                edges=[
                    Edge(node="C", cursor="YXJyYXljb25uZWN0aW9uOjI="),
                    Edge(node="D", cursor="YXJyYXljb25uZWN0aW9uOjM="),
                    Edge(node="E", cursor="YXJyYXljb25uZWN0aW9uOjQ="),
                ],
                pageInfo=PageInfo(
                    startCursor="YXJyYXljb25uZWN0aW9uOjI=",
                    endCursor="YXJyYXljb25uZWN0aW9uOjQ=",
                    hasPreviousPage=False,
                    hasNextPage=False,
                ),
            )

        def respects_last_and_before():
            c = connection_from_array(
                letters, dict(last=2, before="YXJyYXljb25uZWN0aW9uOjM=")
            )
            assert c == Connection(
                edges=[
                    Edge(node="B", cursor="YXJyYXljb25uZWN0aW9uOjE="),
                    Edge(node="C", cursor="YXJyYXljb25uZWN0aW9uOjI="),
                ],
                pageInfo=PageInfo(
                    startCursor="YXJyYXljb25uZWN0aW9uOjE=",
                    endCursor="YXJyYXljb25uZWN0aW9uOjI=",
                    hasPreviousPage=True,
                    hasNextPage=False,
                ),
            )

        def respects_last_and_before_with_long_last():
            c = connection_from_array(
                letters, dict(last=10, before="YXJyYXljb25uZWN0aW9uOjM=")
            )
            assert c == Connection(
                edges=[
                    Edge(node="A", cursor="YXJyYXljb25uZWN0aW9uOjA="),
                    Edge(node="B", cursor="YXJyYXljb25uZWN0aW9uOjE="),
                    Edge(node="C", cursor="YXJyYXljb25uZWN0aW9uOjI="),
                ],
                pageInfo=PageInfo(
                    startCursor="YXJyYXljb25uZWN0aW9uOjA=",
                    endCursor="YXJyYXljb25uZWN0aW9uOjI=",
                    hasPreviousPage=False,
                    hasNextPage=False,
                ),
            )

        def respects_first_and_after_and_before_too_few():
            c = connection_from_array(
                letters,
                dict(
                    first=2,
                    after="YXJyYXljb25uZWN0aW9uOjA=",
                    before="YXJyYXljb25uZWN0aW9uOjQ=",
                ),
            )
            assert c == Connection(
                edges=[
                    Edge(node="B", cursor="YXJyYXljb25uZWN0aW9uOjE="),
                    Edge(node="C", cursor="YXJyYXljb25uZWN0aW9uOjI="),
                ],
                pageInfo=PageInfo(
                    startCursor="YXJyYXljb25uZWN0aW9uOjE=",
                    endCursor="YXJyYXljb25uZWN0aW9uOjI=",
                    hasPreviousPage=False,
                    hasNextPage=True,
                ),
            )

        def respects_first_and_after_and_before_too_many():
            c = connection_from_array(
                letters,
                dict(
                    first=4,
                    after="YXJyYXljb25uZWN0aW9uOjA=",
                    before="YXJyYXljb25uZWN0aW9uOjQ=",
                ),
            )
            assert c == Connection(
                edges=[
                    Edge(node="B", cursor="YXJyYXljb25uZWN0aW9uOjE="),
                    Edge(node="C", cursor="YXJyYXljb25uZWN0aW9uOjI="),
                    Edge(node="D", cursor="YXJyYXljb25uZWN0aW9uOjM="),
                ],
                pageInfo=PageInfo(
                    startCursor="YXJyYXljb25uZWN0aW9uOjE=",
                    endCursor="YXJyYXljb25uZWN0aW9uOjM=",
                    hasPreviousPage=False,
                    hasNextPage=False,
                ),
            )

        def respects_first_and_after_and_before_exactly_right():
            c = connection_from_array(
                letters,
                dict(
                    first=3,
                    after="YXJyYXljb25uZWN0aW9uOjA=",
                    before="YXJyYXljb25uZWN0aW9uOjQ=",
                ),
            )
            assert c == Connection(
                edges=[
                    Edge(node="B", cursor="YXJyYXljb25uZWN0aW9uOjE="),
                    Edge(node="C", cursor="YXJyYXljb25uZWN0aW9uOjI="),
                    Edge(node="D", cursor="YXJyYXljb25uZWN0aW9uOjM="),
                ],
                pageInfo=PageInfo(
                    startCursor="YXJyYXljb25uZWN0aW9uOjE=",
                    endCursor="YXJyYXljb25uZWN0aW9uOjM=",
                    hasPreviousPage=False,
                    hasNextPage=False,
                ),
            )

        def respects_last_and_after_and_before_too_few():
            c = connection_from_array(
                letters,
                dict(
                    last=2,
                    after="YXJyYXljb25uZWN0aW9uOjA=",
                    before="YXJyYXljb25uZWN0aW9uOjQ=",
                ),
            )
            assert c == Connection(
                edges=[
                    Edge(node="C", cursor="YXJyYXljb25uZWN0aW9uOjI="),
                    Edge(node="D", cursor="YXJyYXljb25uZWN0aW9uOjM="),
                ],
                pageInfo=PageInfo(
                    startCursor="YXJyYXljb25uZWN0aW9uOjI=",
                    endCursor="YXJyYXljb25uZWN0aW9uOjM=",
                    hasPreviousPage=True,
                    hasNextPage=False,
                ),
            )

        def respects_last_and_after_and_before_too_many():
            c = connection_from_array(
                letters,
                dict(
                    last=4,
                    after="YXJyYXljb25uZWN0aW9uOjA=",
                    before="YXJyYXljb25uZWN0aW9uOjQ=",
                ),
            )
            assert c == Connection(
                edges=[
                    Edge(node="B", cursor="YXJyYXljb25uZWN0aW9uOjE="),
                    Edge(node="C", cursor="YXJyYXljb25uZWN0aW9uOjI="),
                    Edge(node="D", cursor="YXJyYXljb25uZWN0aW9uOjM="),
                ],
                pageInfo=PageInfo(
                    startCursor="YXJyYXljb25uZWN0aW9uOjE=",
                    endCursor="YXJyYXljb25uZWN0aW9uOjM=",
                    hasPreviousPage=False,
                    hasNextPage=False,
                ),
            )

        def respects_last_and_after_and_before_exactly_right():
            c = connection_from_array(
                letters,
                dict(
                    last=3,
                    after="YXJyYXljb25uZWN0aW9uOjA=",
                    before="YXJyYXljb25uZWN0aW9uOjQ=",
                ),
            )
            assert c == Connection(
                edges=[
                    Edge(node="B", cursor="YXJyYXljb25uZWN0aW9uOjE="),
                    Edge(node="C", cursor="YXJyYXljb25uZWN0aW9uOjI="),
                    Edge(node="D", cursor="YXJyYXljb25uZWN0aW9uOjM="),
                ],
                pageInfo=PageInfo(
                    startCursor="YXJyYXljb25uZWN0aW9uOjE=",
                    endCursor="YXJyYXljb25uZWN0aW9uOjM=",
                    hasPreviousPage=False,
                    hasNextPage=False,
                ),
            )

    def describe_cursor_edge_cases():
        def throws_an_error_if_first_smaller_than_zero():
            with raises(ValueError) as exc_info:
                connection_from_array(letters, dict(first=-1))
            assert str(exc_info.value) == (
                "Argument 'first' must be a non-negative integer."
            )

        def throws_an_error_if_last_smaller_than_zero():
            with raises(ValueError) as exc_info:
                connection_from_array(letters, dict(last=-1))
            assert str(exc_info.value) == (
                "Argument 'last' must be a non-negative integer."
            )

        def returns_all_elements_if_cursors_are_invalid():
            c = connection_from_array(letters, dict(before="invalid", after="invalid"))
            assert c == Connection(
                edges=[
                    Edge(node="A", cursor="YXJyYXljb25uZWN0aW9uOjA="),
                    Edge(node="B", cursor="YXJyYXljb25uZWN0aW9uOjE="),
                    Edge(node="C", cursor="YXJyYXljb25uZWN0aW9uOjI="),
                    Edge(node="D", cursor="YXJyYXljb25uZWN0aW9uOjM="),
                    Edge(node="E", cursor="YXJyYXljb25uZWN0aW9uOjQ="),
                ],
                pageInfo=PageInfo(
                    startCursor="YXJyYXljb25uZWN0aW9uOjA=",
                    endCursor="YXJyYXljb25uZWN0aW9uOjQ=",
                    hasPreviousPage=False,
                    hasNextPage=False,
                ),
            )

        def returns_all_elements_if_cursors_are_on_the_outside():
            c = connection_from_array(
                letters,
                dict(
                    before="YXJyYXljb25uZWN0aW9uOjYK",
                    after="YXJyYXljb25uZWN0aW9uOi0xCg==",
                ),
            )
            assert c == Connection(
                edges=[
                    Edge(node="A", cursor="YXJyYXljb25uZWN0aW9uOjA="),
                    Edge(node="B", cursor="YXJyYXljb25uZWN0aW9uOjE="),
                    Edge(node="C", cursor="YXJyYXljb25uZWN0aW9uOjI="),
                    Edge(node="D", cursor="YXJyYXljb25uZWN0aW9uOjM="),
                    Edge(node="E", cursor="YXJyYXljb25uZWN0aW9uOjQ="),
                ],
                pageInfo=PageInfo(
                    startCursor="YXJyYXljb25uZWN0aW9uOjA=",
                    endCursor="YXJyYXljb25uZWN0aW9uOjQ=",
                    hasPreviousPage=False,
                    hasNextPage=False,
                ),
            )

        def returns_no_elements_if_cursors_cross():
            c = connection_from_array(
                letters,
                dict(
                    before="YXJyYXljb25uZWN0aW9uOjI=", after="YXJyYXljb25uZWN0aW9uOjQ="
                ),
            )
            assert c == Connection(
                edges=[],
                pageInfo=PageInfo(
                    startCursor=None,
                    endCursor=None,
                    hasPreviousPage=False,
                    hasNextPage=False,
                ),
            )

    def describe_cursor_for_object_in_connection():
        def returns_an_edges_cursor_given_an_array_and_a_member_object():
            letter_b_cursor = cursor_for_object_in_connection(letters, "B")
            assert letter_b_cursor == "YXJyYXljb25uZWN0aW9uOjE="

        def returns_null_given_an_array_and_a_non_member_object():
            letter_f_cursor = cursor_for_object_in_connection(letters, "F")
            assert letter_f_cursor is None

        def describe_extended_functionality():
            """Test functionality that is not part of graphql-relay-js."""

            def returns_an_edges_cursor_given_an_array_without_index_method():
                class LettersWithoutIndex:
                    __getitem__ = letters.__getitem__

                letters_without_index = LettersWithoutIndex()

                with raises(AttributeError):
                    cast(Sequence, letters_without_index).index("B")

                letter_b_cursor = cursor_for_object_in_connection(
                    cast(Sequence, letters_without_index), "B"
                )
                assert letter_b_cursor == "YXJyYXljb25uZWN0aW9uOjE="

    def describe_extended_functionality():
        """Test functionality that is not part of graphql-relay-js."""

        def does_not_require_args():
            c = connection_from_array(letters)
            assert c == Connection(
                edges=[
                    Edge(node="A", cursor="YXJyYXljb25uZWN0aW9uOjA="),
                    Edge(node="B", cursor="YXJyYXljb25uZWN0aW9uOjE="),
                    Edge(node="C", cursor="YXJyYXljb25uZWN0aW9uOjI="),
                    Edge(node="D", cursor="YXJyYXljb25uZWN0aW9uOjM="),
                    Edge(node="E", cursor="YXJyYXljb25uZWN0aW9uOjQ="),
                ],
                pageInfo=PageInfo(
                    startCursor="YXJyYXljb25uZWN0aW9uOjA=",
                    endCursor="YXJyYXljb25uZWN0aW9uOjQ=",
                    hasPreviousPage=False,
                    hasNextPage=False,
                ),
            )

        def uses_default_connection_types():
            connection = connection_from_array(letters[:1])
            assert isinstance(connection, Connection)
            edge = connection.edges[0]
            assert isinstance(edge, Edge)
            assert len(connection.edges) == 1
            assert edge == Edge(node="A", cursor="YXJyYXljb25uZWN0aW9uOjA=")
            page_info = connection.pageInfo
            assert isinstance(page_info, PageInfo)
            assert page_info == PageInfo(
                startCursor="YXJyYXljb25uZWN0aW9uOjA=",
                endCursor="YXJyYXljb25uZWN0aW9uOjA=",
                hasPreviousPage=False,
                hasNextPage=False,
            )

        def accepts_custom_connection_type():
            class CustomConnection:
                # noinspection PyPep8Naming
                def __init__(self, edges, pageInfo):
                    self.edges = edges
                    self.page_info = pageInfo

            connection = connection_from_array(
                letters[:1], connection_type=CustomConnection
            )
            assert isinstance(connection, CustomConnection)
            edge = connection.edges[0]
            assert isinstance(edge, Edge)
            assert len(connection.edges) == 1
            assert edge == Edge(node="A", cursor="YXJyYXljb25uZWN0aW9uOjA=")
            page_info = connection.page_info
            assert isinstance(page_info, PageInfo)
            assert page_info == PageInfo(
                startCursor="YXJyYXljb25uZWN0aW9uOjA=",
                endCursor="YXJyYXljb25uZWN0aW9uOjA=",
                hasPreviousPage=False,
                hasNextPage=False,
            )

        def accepts_custom_edge_type():
            class CustomEdge:
                def __init__(self, node, cursor):
                    self.node = node
                    self.cursor = cursor

            connection = connection_from_array(letters[:1], edge_type=CustomEdge)
            assert isinstance(connection, Connection)
            assert isinstance(connection.edges, list)
            assert len(connection.edges) == 1
            edge = connection.edges[0]
            assert isinstance(edge, CustomEdge)
            assert edge.node == "A"
            assert edge.cursor == "YXJyYXljb25uZWN0aW9uOjA="
            page_info = connection.pageInfo
            assert isinstance(page_info, PageInfo)
            assert page_info == PageInfo(
                startCursor="YXJyYXljb25uZWN0aW9uOjA=",
                endCursor="YXJyYXljb25uZWN0aW9uOjA=",
                hasPreviousPage=False,
                hasNextPage=False,
            )

        def accepts_custom_page_info_type():
            class CustomPageInfo:
                # noinspection PyPep8Naming
                def __init__(
                    self, startCursor, endCursor, hasPreviousPage, hasNextPage
                ):
                    self.startCursor = startCursor
                    self.endCursor = endCursor
                    self.hasPreviousPage = hasPreviousPage
                    self.hasNextPage = hasNextPage

            connection = connection_from_array(
                letters[:1], page_info_type=CustomPageInfo
            )
            assert isinstance(connection, Connection)
            assert isinstance(connection.edges, list)
            assert len(connection.edges) == 1
            edge = connection.edges[0]
            assert isinstance(edge, Edge)
            assert edge == Edge(node="A", cursor="YXJyYXljb25uZWN0aW9uOjA=")
            page_info = connection.pageInfo
            assert isinstance(page_info, CustomPageInfo)
            assert page_info.startCursor == "YXJyYXljb25uZWN0aW9uOjA="
            assert page_info.endCursor == "YXJyYXljb25uZWN0aW9uOjA="
            assert page_info.hasPreviousPage is False
            assert page_info.hasNextPage is False

        def provides_deprecated_connection_from_list():
            with deprecated_call():
                # noinspection PyDeprecation
                c = connection_from_list(
                    letters[:1],
                    args={},
                    connection_type=Connection,
                    edge_type=Edge,
                    pageinfo_type=PageInfo,
                )
            assert c == Connection(
                edges=[Edge(node="A", cursor="YXJyYXljb25uZWN0aW9uOjA=")],
                pageInfo=PageInfo(
                    startCursor="YXJyYXljb25uZWN0aW9uOjA=",
                    endCursor="YXJyYXljb25uZWN0aW9uOjA=",
                    hasPreviousPage=False,
                    hasNextPage=False,
                ),
            )


def describe_connection_from_array_slice():
    letters = ["A", "B", "C", "D", "E"]

    def works_with_a_just_right_array_slice():
        c = connection_from_array_slice(
            letters[1:3],
            dict(first=2, after="YXJyYXljb25uZWN0aW9uOjA="),
            slice_start=1,
            array_length=5,
        )
        assert c == Connection(
            edges=[
                Edge(node="B", cursor="YXJyYXljb25uZWN0aW9uOjE="),
                Edge(node="C", cursor="YXJyYXljb25uZWN0aW9uOjI="),
            ],
            pageInfo=PageInfo(
                startCursor="YXJyYXljb25uZWN0aW9uOjE=",
                endCursor="YXJyYXljb25uZWN0aW9uOjI=",
                hasPreviousPage=False,
                hasNextPage=True,
            ),
        )

    def works_with_an_oversized_array_slice_left_side():
        c = connection_from_array_slice(
            letters[0:3],
            dict(first=2, after="YXJyYXljb25uZWN0aW9uOjA="),
            slice_start=0,
            array_length=5,
        )
        assert c == Connection(
            edges=[
                Edge(node="B", cursor="YXJyYXljb25uZWN0aW9uOjE="),
                Edge(node="C", cursor="YXJyYXljb25uZWN0aW9uOjI="),
            ],
            pageInfo=PageInfo(
                startCursor="YXJyYXljb25uZWN0aW9uOjE=",
                endCursor="YXJyYXljb25uZWN0aW9uOjI=",
                hasPreviousPage=False,
                hasNextPage=True,
            ),
        )

    def works_with_an_oversized_array_slice_right_side():
        c = connection_from_array_slice(
            letters[2:4],
            dict(first=1, after="YXJyYXljb25uZWN0aW9uOjE="),
            slice_start=2,
            array_length=5,
        )
        assert c == Connection(
            edges=[Edge(node="C", cursor="YXJyYXljb25uZWN0aW9uOjI=")],
            pageInfo=PageInfo(
                startCursor="YXJyYXljb25uZWN0aW9uOjI=",
                endCursor="YXJyYXljb25uZWN0aW9uOjI=",
                hasPreviousPage=False,
                hasNextPage=True,
            ),
        )

    def works_with_an_oversized_array_slice_both_sides():
        c = connection_from_array_slice(
            letters[1:4],
            dict(first=1, after="YXJyYXljb25uZWN0aW9uOjE="),
            slice_start=1,
            array_length=5,
        )
        assert c == Connection(
            edges=[Edge(node="C", cursor="YXJyYXljb25uZWN0aW9uOjI=")],
            pageInfo=PageInfo(
                startCursor="YXJyYXljb25uZWN0aW9uOjI=",
                endCursor="YXJyYXljb25uZWN0aW9uOjI=",
                hasPreviousPage=False,
                hasNextPage=True,
            ),
        )

    def works_with_an_undersized_array_slice_left_side():
        c = connection_from_array_slice(
            letters[3:5],
            dict(first=3, after="YXJyYXljb25uZWN0aW9uOjE="),
            slice_start=3,
            array_length=5,
        )
        assert c == Connection(
            edges=[
                Edge(node="D", cursor="YXJyYXljb25uZWN0aW9uOjM="),
                Edge(node="E", cursor="YXJyYXljb25uZWN0aW9uOjQ="),
            ],
            pageInfo=PageInfo(
                startCursor="YXJyYXljb25uZWN0aW9uOjM=",
                endCursor="YXJyYXljb25uZWN0aW9uOjQ=",
                hasPreviousPage=False,
                hasNextPage=False,
            ),
        )

    def works_with_an_undersized_array_slice_right_side():
        c = connection_from_array_slice(
            letters[2:4],
            dict(first=3, after="YXJyYXljb25uZWN0aW9uOjE="),
            slice_start=2,
            array_length=5,
        )
        assert c == Connection(
            edges=[
                Edge(node="C", cursor="YXJyYXljb25uZWN0aW9uOjI="),
                Edge(node="D", cursor="YXJyYXljb25uZWN0aW9uOjM="),
            ],
            pageInfo=PageInfo(
                startCursor="YXJyYXljb25uZWN0aW9uOjI=",
                endCursor="YXJyYXljb25uZWN0aW9uOjM=",
                hasPreviousPage=False,
                hasNextPage=True,
            ),
        )

    def works_with_an_undersized_array_slice_both_sides():
        c = connection_from_array_slice(
            letters[3:4],
            dict(first=3, after="YXJyYXljb25uZWN0aW9uOjE="),
            slice_start=3,
            array_length=5,
        )
        assert c == Connection(
            edges=[Edge(node="D", cursor="YXJyYXljb25uZWN0aW9uOjM=")],
            pageInfo=PageInfo(
                startCursor="YXJyYXljb25uZWN0aW9uOjM=",
                endCursor="YXJyYXljb25uZWN0aW9uOjM=",
                hasPreviousPage=False,
                hasNextPage=True,
            ),
        )

    def describe_extended_functionality():
        """Test functionality that is not part of graphql-relay-js."""

        def does_not_require_args():
            c = connection_from_array_slice(letters, slice_start=0, array_length=5)
            assert c == Connection(
                edges=[
                    Edge(node="A", cursor="YXJyYXljb25uZWN0aW9uOjA="),
                    Edge(node="B", cursor="YXJyYXljb25uZWN0aW9uOjE="),
                    Edge(node="C", cursor="YXJyYXljb25uZWN0aW9uOjI="),
                    Edge(node="D", cursor="YXJyYXljb25uZWN0aW9uOjM="),
                    Edge(node="E", cursor="YXJyYXljb25uZWN0aW9uOjQ="),
                ],
                pageInfo=PageInfo(
                    startCursor="YXJyYXljb25uZWN0aW9uOjA=",
                    endCursor="YXJyYXljb25uZWN0aW9uOjQ=",
                    hasPreviousPage=False,
                    hasNextPage=False,
                ),
            )

        def uses_zero_as_default_for_slice_start():
            c = connection_from_array_slice(letters[:1], dict(first=1), array_length=5)
            assert c == Connection(
                edges=[Edge(node="A", cursor="YXJyYXljb25uZWN0aW9uOjA=")],
                pageInfo=PageInfo(
                    startCursor="YXJyYXljb25uZWN0aW9uOjA=",
                    endCursor="YXJyYXljb25uZWN0aW9uOjA=",
                    hasPreviousPage=False,
                    hasNextPage=True,
                ),
            )

        def uses_slice_end_as_default_for_array_length():
            c = connection_from_array_slice(letters[:1], dict(first=1), slice_start=0)
            assert c == Connection(
                edges=[Edge(node="A", cursor="YXJyYXljb25uZWN0aW9uOjA=")],
                pageInfo=PageInfo(
                    startCursor="YXJyYXljb25uZWN0aW9uOjA=",
                    endCursor="YXJyYXljb25uZWN0aW9uOjA=",
                    hasPreviousPage=False,
                    hasNextPage=False,
                ),
            )

        def ignores_len_of_slice_if_array_slice_length_provided():
            c = connection_from_array_slice(
                letters[:2], dict(first=2), array_length=2, array_slice_length=1
            )
            assert c == Connection(
                edges=[Edge(node="A", cursor="YXJyYXljb25uZWN0aW9uOjA=")],
                pageInfo=PageInfo(
                    startCursor="YXJyYXljb25uZWN0aW9uOjA=",
                    endCursor="YXJyYXljb25uZWN0aW9uOjA=",
                    hasPreviousPage=False,
                    hasNextPage=True,
                ),
            )

        def uses_array_slice_length_instead_of_len_function():
            class LettersWithoutLen:
                __getitem__ = letters.__getitem__

            letters_without_len = LettersWithoutLen()

            with raises(TypeError):
                len(cast(Sequence, letters_without_len))

            with raises(TypeError):
                connection_from_array_slice(letters_without_len)

            c = connection_from_array_slice(letters_without_len, array_slice_length=5)
            assert c == Connection(
                edges=[
                    Edge(node="A", cursor="YXJyYXljb25uZWN0aW9uOjA="),
                    Edge(node="B", cursor="YXJyYXljb25uZWN0aW9uOjE="),
                    Edge(node="C", cursor="YXJyYXljb25uZWN0aW9uOjI="),
                    Edge(node="D", cursor="YXJyYXljb25uZWN0aW9uOjM="),
                    Edge(node="E", cursor="YXJyYXljb25uZWN0aW9uOjQ="),
                ],
                pageInfo=PageInfo(
                    startCursor="YXJyYXljb25uZWN0aW9uOjA=",
                    endCursor="YXJyYXljb25uZWN0aW9uOjQ=",
                    hasPreviousPage=False,
                    hasNextPage=False,
                ),
            )

        def uses_default_connection_types():
            connection = connection_from_array_slice(
                letters[:1], slice_start=0, array_length=1
            )
            assert isinstance(connection, Connection)
            edge = connection.edges[0]
            assert isinstance(edge, Edge)
            assert len(connection.edges) == 1
            assert edge == Edge(node="A", cursor="YXJyYXljb25uZWN0aW9uOjA=")
            page_info = connection.pageInfo
            assert isinstance(page_info, PageInfo)
            assert page_info == PageInfo(
                startCursor="YXJyYXljb25uZWN0aW9uOjA=",
                endCursor="YXJyYXljb25uZWN0aW9uOjA=",
                hasPreviousPage=False,
                hasNextPage=False,
            )

        def accepts_custom_connection_type():
            class CustomConnection:
                # noinspection PyPep8Naming
                def __init__(self, edges, pageInfo):
                    self.edges = edges
                    self.page_info = pageInfo

            connection = connection_from_array_slice(
                letters[:1],
                slice_start=0,
                array_length=1,
                connection_type=CustomConnection,
            )
            assert isinstance(connection, CustomConnection)
            edge = connection.edges[0]
            assert isinstance(edge, Edge)
            assert len(connection.edges) == 1
            assert edge == Edge(node="A", cursor="YXJyYXljb25uZWN0aW9uOjA=")
            page_info = connection.page_info
            assert isinstance(page_info, PageInfo)
            assert page_info == PageInfo(
                startCursor="YXJyYXljb25uZWN0aW9uOjA=",
                endCursor="YXJyYXljb25uZWN0aW9uOjA=",
                hasPreviousPage=False,
                hasNextPage=False,
            )

        def accepts_custom_edge_type():
            class CustomEdge:
                def __init__(self, node, cursor):
                    self.node = node
                    self.cursor = cursor

            connection = connection_from_array_slice(
                letters[:1], slice_start=0, array_length=1, edge_type=CustomEdge
            )
            assert isinstance(connection, Connection)
            assert isinstance(connection.edges, list)
            assert len(connection.edges) == 1
            edge = connection.edges[0]
            assert isinstance(edge, CustomEdge)
            assert edge.node == "A"
            assert edge.cursor == "YXJyYXljb25uZWN0aW9uOjA="
            page_info = connection.pageInfo
            assert isinstance(page_info, PageInfo)
            assert page_info == PageInfo(
                startCursor="YXJyYXljb25uZWN0aW9uOjA=",
                endCursor="YXJyYXljb25uZWN0aW9uOjA=",
                hasPreviousPage=False,
                hasNextPage=False,
            )

        def accepts_custom_page_info_type():
            class CustomPageInfo:
                # noinspection PyPep8Naming
                def __init__(
                    self, startCursor, endCursor, hasPreviousPage, hasNextPage
                ):
                    self.startCursor = startCursor
                    self.endCursor = endCursor
                    self.hasPreviousPage = hasPreviousPage
                    self.hasNextPage = hasNextPage

            connection = connection_from_array_slice(
                letters[:1],
                slice_start=0,
                array_length=1,
                page_info_type=CustomPageInfo,
            )
            assert isinstance(connection, Connection)
            assert isinstance(connection.edges, list)
            assert len(connection.edges) == 1
            edge = connection.edges[0]
            assert isinstance(edge, Edge)
            assert edge == Edge(node="A", cursor="YXJyYXljb25uZWN0aW9uOjA=")
            page_info = connection.pageInfo
            assert isinstance(page_info, CustomPageInfo)
            assert page_info.startCursor == "YXJyYXljb25uZWN0aW9uOjA="
            assert page_info.endCursor == "YXJyYXljb25uZWN0aW9uOjA="
            assert page_info.hasPreviousPage is False
            assert page_info.hasNextPage is False

        def provides_deprecated_connection_from_list_slice():
            with deprecated_call():
                # noinspection PyDeprecation
                c = connection_from_list_slice(
                    letters[:1],
                    args={},
                    connection_type=Connection,
                    edge_type=Edge,
                    pageinfo_type=PageInfo,
                    slice_start=0,
                    list_length=1,
                    list_slice_length=1,
                )
            assert c == Connection(
                edges=[Edge(node="A", cursor="YXJyYXljb25uZWN0aW9uOjA=")],
                pageInfo=PageInfo(
                    startCursor="YXJyYXljb25uZWN0aW9uOjA=",
                    endCursor="YXJyYXljb25uZWN0aW9uOjA=",
                    hasPreviousPage=False,
                    hasNextPage=False,
                ),
            )
