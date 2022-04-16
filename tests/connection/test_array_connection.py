from typing import cast, Sequence

from pytest import deprecated_call, raises

from graphql_relay import (
    connection_from_array,
    connection_from_array_slice,
    cursor_for_object_in_connection,
    offset_to_cursor,
    Connection,
    Edge,
    PageInfo,
)

array_abcde = ["A", "B", "C", "D", "E"]

cursor_a = "YXJyYXljb25uZWN0aW9uOjA="
cursor_b = "YXJyYXljb25uZWN0aW9uOjE="
cursor_c = "YXJyYXljb25uZWN0aW9uOjI="
cursor_d = "YXJyYXljb25uZWN0aW9uOjM="
cursor_e = "YXJyYXljb25uZWN0aW9uOjQ="

edge_a = Edge(node="A", cursor=cursor_a)
edge_b = Edge(node="B", cursor=cursor_b)
edge_c = Edge(node="C", cursor=cursor_c)
edge_d = Edge(node="D", cursor=cursor_d)
edge_e = Edge(node="E", cursor=cursor_e)


def describe_connection_from_array():
    def warns_for_deprecated_import():
        from importlib import reload

        with deprecated_call():
            from graphql_relay.connection import arrayconnection as deprecated

            # noinspection PyDeprecation
            reload(deprecated)
        # noinspection PyDeprecation
        assert deprecated.connection_from_array is connection_from_array

    def describe_basic_slicing():
        def returns_all_elements_without_filters():
            c = connection_from_array(array_abcde, {})
            assert c == Connection(
                edges=[edge_a, edge_b, edge_c, edge_d, edge_e],
                pageInfo=PageInfo(
                    startCursor=cursor_a,
                    endCursor=cursor_e,
                    hasPreviousPage=False,
                    hasNextPage=False,
                ),
            )

        def respects_a_smaller_first():
            c = connection_from_array(array_abcde, dict(first=2))
            assert c == Connection(
                edges=[
                    edge_a,
                    edge_b,
                ],
                pageInfo=PageInfo(
                    startCursor=cursor_a,
                    endCursor=cursor_b,
                    hasPreviousPage=False,
                    hasNextPage=True,
                ),
            )

        def respects_an_overly_large_first():
            c = connection_from_array(array_abcde, dict(first=10))
            assert c == Connection(
                edges=[edge_a, edge_b, edge_c, edge_d, edge_e],
                pageInfo=PageInfo(
                    startCursor=cursor_a,
                    endCursor=cursor_e,
                    hasPreviousPage=False,
                    hasNextPage=False,
                ),
            )

        def respects_a_smaller_last():
            c = connection_from_array(array_abcde, dict(last=2))
            assert c == Connection(
                edges=[edge_d, edge_e],
                pageInfo=PageInfo(
                    startCursor=cursor_d,
                    endCursor=cursor_e,
                    hasPreviousPage=True,
                    hasNextPage=False,
                ),
            )

        def respects_an_overly_large_last():
            c = connection_from_array(array_abcde, dict(last=10))
            assert c == Connection(
                edges=[edge_a, edge_b, edge_c, edge_d, edge_e],
                pageInfo=PageInfo(
                    startCursor=cursor_a,
                    endCursor=cursor_e,
                    hasPreviousPage=False,
                    hasNextPage=False,
                ),
            )

    def describe_pagination():
        def respects_first_and_after():
            c = connection_from_array(array_abcde, dict(first=2, after=cursor_b))
            assert c == Connection(
                edges=[edge_c, edge_d],
                pageInfo=PageInfo(
                    startCursor=cursor_c,
                    endCursor=cursor_d,
                    hasPreviousPage=False,
                    hasNextPage=True,
                ),
            )

        def respects_first_and_after_with_long_first():
            c = connection_from_array(array_abcde, dict(first=10, after=cursor_b))
            assert c == Connection(
                edges=[edge_c, edge_d, edge_e],
                pageInfo=PageInfo(
                    startCursor=cursor_c,
                    endCursor=cursor_e,
                    hasPreviousPage=False,
                    hasNextPage=False,
                ),
            )

        def respects_last_and_before():
            c = connection_from_array(array_abcde, dict(last=2, before=cursor_d))
            assert c == Connection(
                edges=[edge_b, edge_c],
                pageInfo=PageInfo(
                    startCursor=cursor_b,
                    endCursor=cursor_c,
                    hasPreviousPage=True,
                    hasNextPage=False,
                ),
            )

        def respects_last_and_before_with_long_last():
            c = connection_from_array(array_abcde, dict(last=10, before=cursor_d))
            assert c == Connection(
                edges=[edge_a, edge_b, edge_c],
                pageInfo=PageInfo(
                    startCursor=cursor_a,
                    endCursor=cursor_c,
                    hasPreviousPage=False,
                    hasNextPage=False,
                ),
            )

        def respects_first_and_after_and_before_too_few():
            c = connection_from_array(
                array_abcde,
                dict(first=2, after=cursor_a, before=cursor_e),
            )
            assert c == Connection(
                edges=[edge_b, edge_c],
                pageInfo=PageInfo(
                    startCursor=cursor_b,
                    endCursor=cursor_c,
                    hasPreviousPage=False,
                    hasNextPage=True,
                ),
            )

        def respects_first_and_after_and_before_too_many():
            c = connection_from_array(
                array_abcde,
                dict(first=4, after=cursor_a, before=cursor_e),
            )
            assert c == Connection(
                edges=[edge_b, edge_c, edge_d],
                pageInfo=PageInfo(
                    startCursor=cursor_b,
                    endCursor=cursor_d,
                    hasPreviousPage=False,
                    hasNextPage=False,
                ),
            )

        def respects_first_and_after_and_before_exactly_right():
            c = connection_from_array(
                array_abcde,
                dict(first=3, after=cursor_a, before=cursor_e),
            )
            assert c == Connection(
                edges=[edge_b, edge_c, edge_d],
                pageInfo=PageInfo(
                    startCursor=cursor_b,
                    endCursor=cursor_d,
                    hasPreviousPage=False,
                    hasNextPage=False,
                ),
            )

        def respects_last_and_after_and_before_too_few():
            c = connection_from_array(
                array_abcde,
                dict(last=2, after=cursor_a, before=cursor_e),
            )
            assert c == Connection(
                edges=[edge_c, edge_d],
                pageInfo=PageInfo(
                    startCursor=cursor_c,
                    endCursor=cursor_d,
                    hasPreviousPage=True,
                    hasNextPage=False,
                ),
            )

        def respects_last_and_after_and_before_too_many():
            c = connection_from_array(
                array_abcde,
                dict(last=4, after=cursor_a, before=cursor_e),
            )
            assert c == Connection(
                edges=[edge_b, edge_c, edge_d],
                pageInfo=PageInfo(
                    startCursor=cursor_b,
                    endCursor=cursor_d,
                    hasPreviousPage=False,
                    hasNextPage=False,
                ),
            )

        def respects_last_and_after_and_before_exactly_right():
            c = connection_from_array(
                array_abcde,
                dict(last=3, after=cursor_a, before=cursor_e),
            )
            assert c == Connection(
                edges=[edge_b, edge_c, edge_d],
                pageInfo=PageInfo(
                    startCursor=cursor_b,
                    endCursor=cursor_d,
                    hasPreviousPage=False,
                    hasNextPage=False,
                ),
            )

    def describe_cursor_edge_cases():
        def throws_an_error_if_first_smaller_than_zero():
            with raises(ValueError) as exc_info:
                connection_from_array(array_abcde, dict(first=-1))
            assert str(exc_info.value) == (
                "Argument 'first' must be a non-negative integer."
            )

        def throws_an_error_if_last_smaller_than_zero():
            with raises(ValueError) as exc_info:
                connection_from_array(array_abcde, dict(last=-1))
            assert str(exc_info.value) == (
                "Argument 'last' must be a non-negative integer."
            )

        def returns_all_elements_if_cursors_are_invalid():
            c1 = connection_from_array(
                array_abcde, dict(before="InvalidBase64", after="InvalidBase64")
            )

            invalid_unicode_in_base64 = "9JCAgA=="  # U+110000
            c2 = connection_from_array(
                array_abcde,
                dict(before=invalid_unicode_in_base64, after=invalid_unicode_in_base64),
            )

            assert c1 == c2
            assert c1 == Connection(
                edges=[edge_a, edge_b, edge_c, edge_d, edge_e],
                pageInfo=PageInfo(
                    startCursor=cursor_a,
                    endCursor=cursor_e,
                    hasPreviousPage=False,
                    hasNextPage=False,
                ),
            )

        def returns_all_elements_if_cursors_are_on_the_outside():
            all_edges = Connection(
                edges=[edge_a, edge_b, edge_c, edge_d, edge_e],
                pageInfo=PageInfo(
                    startCursor=cursor_a,
                    endCursor=cursor_e,
                    hasPreviousPage=False,
                    hasNextPage=False,
                ),
            )

            assert (
                connection_from_array(array_abcde, dict(before=offset_to_cursor(6)))
                == all_edges
            )
            assert (
                connection_from_array(array_abcde, dict(before=offset_to_cursor(-1)))
                == all_edges
            )
            assert (
                connection_from_array(array_abcde, dict(after=offset_to_cursor(6)))
                == all_edges
            )
            assert (
                connection_from_array(array_abcde, dict(after=offset_to_cursor(-1)))
                == all_edges
            )

        def returns_no_elements_if_cursors_cross():
            c = connection_from_array(
                array_abcde,
                dict(before=cursor_c, after=cursor_e),
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
            letter_b_cursor = cursor_for_object_in_connection(array_abcde, "B")
            assert letter_b_cursor == cursor_b

        def returns_null_given_an_array_and_a_non_member_object():
            letter_f_cursor = cursor_for_object_in_connection(array_abcde, "F")
            assert letter_f_cursor is None

        def describe_extended_functionality():
            """Test functionality that is not part of graphql-relay-js."""

            def returns_an_edges_cursor_given_an_array_without_index_method():
                class LettersWithoutIndex:
                    __getitem__ = array_abcde.__getitem__

                letters_without_index = cast(Sequence, LettersWithoutIndex())

                with raises(AttributeError):
                    letters_without_index.index("B")

                letter_b_cursor = cursor_for_object_in_connection(
                    letters_without_index, "B"
                )
                assert letter_b_cursor == cursor_b

                no_letter_cursor = cursor_for_object_in_connection(
                    letters_without_index, "="
                )
                assert no_letter_cursor is None

    def describe_extended_functionality():
        """Test functionality that is not part of graphql-relay-js."""

        def does_not_require_args():
            c = connection_from_array(array_abcde)
            assert c == Connection(
                edges=[edge_a, edge_b, edge_c, edge_d, edge_e],
                pageInfo=PageInfo(
                    startCursor=cursor_a,
                    endCursor=cursor_e,
                    hasPreviousPage=False,
                    hasNextPage=False,
                ),
            )

        def uses_default_connection_types():
            connection = connection_from_array(array_abcde[:1])
            assert isinstance(connection, Connection)
            edge = connection.edges[0]
            assert isinstance(edge, Edge)
            assert len(connection.edges) == 1
            assert edge == edge_a
            page_info = connection.pageInfo
            assert isinstance(page_info, PageInfo)
            assert page_info == PageInfo(
                startCursor=cursor_a,
                endCursor=cursor_a,
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
                array_abcde[:1], connection_type=CustomConnection
            )
            assert isinstance(connection, CustomConnection)
            edge = connection.edges[0]
            assert isinstance(edge, Edge)
            assert len(connection.edges) == 1
            assert edge == edge_a
            page_info = connection.page_info
            assert isinstance(page_info, PageInfo)
            assert page_info == PageInfo(
                startCursor=cursor_a,
                endCursor=cursor_a,
                hasPreviousPage=False,
                hasNextPage=False,
            )

        def accepts_custom_edge_type():
            class CustomEdge:
                def __init__(self, node, cursor):
                    self.node = node
                    self.cursor = cursor

            connection = connection_from_array(array_abcde[:1], edge_type=CustomEdge)
            assert isinstance(connection, Connection)
            assert isinstance(connection.edges, list)
            assert len(connection.edges) == 1
            edge = connection.edges[0]
            assert isinstance(edge, CustomEdge)
            assert edge.node == "A"
            assert edge.cursor == cursor_a
            page_info = connection.pageInfo
            assert isinstance(page_info, PageInfo)
            assert page_info == PageInfo(
                startCursor=cursor_a,
                endCursor=cursor_a,
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
                array_abcde[:1], page_info_type=CustomPageInfo
            )
            assert isinstance(connection, Connection)
            assert isinstance(connection.edges, list)
            assert len(connection.edges) == 1
            edge = connection.edges[0]
            assert isinstance(edge, Edge)
            assert edge == edge_a
            page_info = connection.pageInfo
            assert isinstance(page_info, CustomPageInfo)
            assert page_info.startCursor == cursor_a
            assert page_info.endCursor == cursor_a
            assert page_info.hasPreviousPage is False
            assert page_info.hasNextPage is False


def describe_connection_from_array_slice():
    def warns_for_deprecated_import():
        from importlib import reload

        with deprecated_call():
            from graphql_relay.connection import arrayconnection as deprecated

            # noinspection PyDeprecation
            reload(deprecated)
        # noinspection PyDeprecation
        assert deprecated.connection_from_array_slice is connection_from_array_slice

    def works_with_a_just_right_array_slice():
        c = connection_from_array_slice(
            array_abcde[1:3],
            dict(first=2, after=cursor_a),
            slice_start=1,
            array_length=5,
        )
        assert c == Connection(
            edges=[edge_b, edge_c],
            pageInfo=PageInfo(
                startCursor=cursor_b,
                endCursor=cursor_c,
                hasPreviousPage=False,
                hasNextPage=True,
            ),
        )

    def works_with_an_oversized_array_slice_left_side():
        c = connection_from_array_slice(
            array_abcde[0:3],
            dict(first=2, after=cursor_a),
            slice_start=0,
            array_length=5,
        )
        assert c == Connection(
            edges=[edge_b, edge_c],
            pageInfo=PageInfo(
                startCursor=cursor_b,
                endCursor=cursor_c,
                hasPreviousPage=False,
                hasNextPage=True,
            ),
        )

    def works_with_an_oversized_array_slice_right_side():
        c = connection_from_array_slice(
            array_abcde[2:4],
            dict(first=1, after=cursor_b),
            slice_start=2,
            array_length=5,
        )
        assert c == Connection(
            edges=[edge_c],
            pageInfo=PageInfo(
                startCursor=cursor_c,
                endCursor=cursor_c,
                hasPreviousPage=False,
                hasNextPage=True,
            ),
        )

    def works_with_an_oversized_array_slice_both_sides():
        c = connection_from_array_slice(
            array_abcde[1:4],
            dict(first=1, after=cursor_b),
            slice_start=1,
            array_length=5,
        )
        assert c == Connection(
            edges=[edge_c],
            pageInfo=PageInfo(
                startCursor=cursor_c,
                endCursor=cursor_c,
                hasPreviousPage=False,
                hasNextPage=True,
            ),
        )

    def works_with_an_undersized_array_slice_left_side():
        c = connection_from_array_slice(
            array_abcde[3:5],
            dict(first=3, after=cursor_b),
            slice_start=3,
            array_length=5,
        )
        assert c == Connection(
            edges=[edge_d, edge_e],
            pageInfo=PageInfo(
                startCursor=cursor_d,
                endCursor=cursor_e,
                hasPreviousPage=False,
                hasNextPage=False,
            ),
        )

    def works_with_an_undersized_array_slice_right_side():
        c = connection_from_array_slice(
            array_abcde[2:4],
            dict(first=3, after=cursor_b),
            slice_start=2,
            array_length=5,
        )
        assert c == Connection(
            edges=[edge_c, edge_d],
            pageInfo=PageInfo(
                startCursor=cursor_c,
                endCursor=cursor_d,
                hasPreviousPage=False,
                hasNextPage=True,
            ),
        )

    def works_with_an_undersized_array_slice_both_sides():
        c = connection_from_array_slice(
            array_abcde[3:4],
            dict(first=3, after=cursor_b),
            slice_start=3,
            array_length=5,
        )
        assert c == Connection(
            edges=[edge_d],
            pageInfo=PageInfo(
                startCursor=cursor_d,
                endCursor=cursor_d,
                hasPreviousPage=False,
                hasNextPage=True,
            ),
        )

    def describe_extended_functionality():
        """Test functionality that is not part of graphql-relay-js."""

        def does_not_require_args():
            c = connection_from_array_slice(array_abcde, slice_start=0, array_length=5)
            assert c == Connection(
                edges=[edge_a, edge_b, edge_c, edge_d, edge_e],
                pageInfo=PageInfo(
                    startCursor=cursor_a,
                    endCursor=cursor_e,
                    hasPreviousPage=False,
                    hasNextPage=False,
                ),
            )

        def uses_zero_as_default_for_slice_start():
            c = connection_from_array_slice(
                array_abcde[:1], dict(first=1), array_length=5
            )
            assert c == Connection(
                edges=[edge_a],
                pageInfo=PageInfo(
                    startCursor=cursor_a,
                    endCursor=cursor_a,
                    hasPreviousPage=False,
                    hasNextPage=True,
                ),
            )

        def uses_slice_end_as_default_for_array_length():
            c = connection_from_array_slice(
                array_abcde[:1], dict(first=1), slice_start=0
            )
            assert c == Connection(
                edges=[edge_a],
                pageInfo=PageInfo(
                    startCursor=cursor_a,
                    endCursor=cursor_a,
                    hasPreviousPage=False,
                    hasNextPage=False,
                ),
            )

        def ignores_len_of_slice_if_array_slice_length_provided():
            c = connection_from_array_slice(
                array_abcde[:2], dict(first=2), array_length=2, array_slice_length=1
            )
            assert c == Connection(
                edges=[edge_a],
                pageInfo=PageInfo(
                    startCursor=cursor_a,
                    endCursor=cursor_a,
                    hasPreviousPage=False,
                    hasNextPage=True,
                ),
            )

        def uses_array_slice_length_instead_of_len_function():
            class LettersWithoutLen:
                __getitem__ = array_abcde.__getitem__

            letters_without_len = cast(Sequence, LettersWithoutLen())

            with raises(TypeError):
                len(letters_without_len)

            with raises(TypeError):
                connection_from_array_slice(letters_without_len)

            c = connection_from_array_slice(letters_without_len, array_slice_length=5)
            assert c == Connection(
                edges=[edge_a, edge_b, edge_c, edge_d, edge_e],
                pageInfo=PageInfo(
                    startCursor=cursor_a,
                    endCursor=cursor_e,
                    hasPreviousPage=False,
                    hasNextPage=False,
                ),
            )

        def uses_default_connection_types():
            connection = connection_from_array_slice(
                array_abcde[:1], slice_start=0, array_length=1
            )
            assert isinstance(connection, Connection)
            edge = connection.edges[0]
            assert isinstance(edge, Edge)
            assert len(connection.edges) == 1
            assert edge == edge_a
            page_info = connection.pageInfo
            assert isinstance(page_info, PageInfo)
            assert page_info == PageInfo(
                startCursor=cursor_a,
                endCursor=cursor_a,
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
                array_abcde[:1],
                slice_start=0,
                array_length=1,
                connection_type=CustomConnection,
            )
            assert isinstance(connection, CustomConnection)
            edge = connection.edges[0]
            assert isinstance(edge, Edge)
            assert len(connection.edges) == 1
            assert edge == edge_a
            page_info = connection.page_info
            assert isinstance(page_info, PageInfo)
            assert page_info == PageInfo(
                startCursor=cursor_a,
                endCursor=cursor_a,
                hasPreviousPage=False,
                hasNextPage=False,
            )

        def accepts_custom_edge_type():
            class CustomEdge:
                def __init__(self, node, cursor):
                    self.node = node
                    self.cursor = cursor

            connection = connection_from_array_slice(
                array_abcde[:1], slice_start=0, array_length=1, edge_type=CustomEdge
            )
            assert isinstance(connection, Connection)
            assert isinstance(connection.edges, list)
            assert len(connection.edges) == 1
            edge = connection.edges[0]
            assert isinstance(edge, CustomEdge)
            assert edge.node == "A"
            assert edge.cursor == cursor_a
            page_info = connection.pageInfo
            assert isinstance(page_info, PageInfo)
            assert page_info == PageInfo(
                startCursor=cursor_a,
                endCursor=cursor_a,
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
                array_abcde[:1],
                slice_start=0,
                array_length=1,
                page_info_type=CustomPageInfo,
            )
            assert isinstance(connection, Connection)
            assert isinstance(connection.edges, list)
            assert len(connection.edges) == 1
            edge = connection.edges[0]
            assert isinstance(edge, Edge)
            assert edge == edge_a
            page_info = connection.pageInfo
            assert isinstance(page_info, CustomPageInfo)
            assert page_info.startCursor == cursor_a
            assert page_info.endCursor == cursor_a
            assert page_info.hasPreviousPage is False
            assert page_info.hasNextPage is False
