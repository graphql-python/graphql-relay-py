from graphql import graphql_sync

from .star_wars_schema import StarWarsSchema as schema


def describe_star_wars_connections():
    def fetches_the_first_ship_of_the_rebels():
        source = """
            {
              rebels {
                name,
                ships(first: 1) {
                  edges {
                    node {
                      name
                    }
                  }
                }
              }
            }
            """
        expected = {
            "rebels": {
                "name": "Alliance to Restore the Republic",
                "ships": {"edges": [{"node": {"name": "X-Wing"}}]},
            }
        }
        result = graphql_sync(schema, source)
        assert result == (expected, None)

    def fetches_the_first_two_ships_of_the_rebels_with_a_cursor():
        source = """
            {
              rebels {
                name,
                ships(first: 2) {
                  edges {
                    cursor,
                    node {
                      name
                    }
                  }
                }
              }
            }
            """
        expected = {
            "rebels": {
                "name": "Alliance to Restore the Republic",
                "ships": {
                    "edges": [
                        {
                            "cursor": "YXJyYXljb25uZWN0aW9uOjA=",
                            "node": {"name": "X-Wing"},
                        },
                        {
                            "cursor": "YXJyYXljb25uZWN0aW9uOjE=",
                            "node": {"name": "Y-Wing"},
                        },
                    ]
                },
            }
        }
        result = graphql_sync(schema, source)
        assert result == (expected, None)

    def fetches_the_next_three_ships_of_the_rebels_with_a_cursor():
        source = """
            {
              rebels {
                name,
                ships(first: 3 after: "YXJyYXljb25uZWN0aW9uOjE=") {
                  edges {
                    cursor,
                    node {
                      name
                    }
                  }
                }
              }
            }
            """
        expected = {
            "rebels": {
                "name": "Alliance to Restore the Republic",
                "ships": {
                    "edges": [
                        {
                            "cursor": "YXJyYXljb25uZWN0aW9uOjI=",
                            "node": {"name": "A-Wing"},
                        },
                        {
                            "cursor": "YXJyYXljb25uZWN0aW9uOjM=",
                            "node": {"name": "Millennium Falcon"},
                        },
                        {
                            "cursor": "YXJyYXljb25uZWN0aW9uOjQ=",
                            "node": {"name": "Home One"},
                        },
                    ]
                },
            }
        }
        result = graphql_sync(schema, source)
        assert result == (expected, None)

    def fetches_no_ships_of_the_rebels_at_the_end_of_connection():
        source = """
            {
              rebels {
                name,
                ships(first: 3 after: "YXJyYXljb25uZWN0aW9uOjQ=") {
                  edges {
                    cursor,
                    node {
                      name
                    }
                  }
                }
              }
            }
            """
        expected = {
            "rebels": {
                "name": "Alliance to Restore the Republic",
                "ships": {"edges": []},
            }
        }
        result = graphql_sync(schema, source)
        assert result == (expected, None)

    def identifies_the_end_of_the_list():
        source = """
            {
              rebels {
                name,
                originalShips: ships(first: 2) {
                  edges {
                    node {
                      name
                    }
                  }
                  pageInfo {
                    hasNextPage
                  }
                }
                moreShips: ships(first: 3 after: "YXJyYXljb25uZWN0aW9uOjE=") {
                  edges {
                    node {
                      name
                    }
                  }
                  pageInfo {
                    hasNextPage
                  }
                }
              }
            }
            """
        expected = {
            "rebels": {
                "name": "Alliance to Restore the Republic",
                "originalShips": {
                    "edges": [
                        {
                            "node": {"name": "X-Wing"},
                        },
                        {
                            "node": {"name": "Y-Wing"},
                        },
                    ],
                    "pageInfo": {"hasNextPage": True},
                },
                "moreShips": {
                    "edges": [
                        {
                            "node": {"name": "A-Wing"},
                        },
                        {
                            "node": {"name": "Millennium Falcon"},
                        },
                        {
                            "node": {"name": "Home One"},
                        },
                    ],
                    "pageInfo": {"hasNextPage": False},
                },
            },
        }
        result = graphql_sync(schema, source)
        assert result == (expected, None)
