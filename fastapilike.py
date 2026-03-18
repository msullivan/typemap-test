from typing import (
    Callable,
    Literal,
    Union,
    ReadOnly,
    TypedDict,
    Never,
    Self,
    TYPE_CHECKING,
)

import typemap_extensions as typing


class FieldArgs(TypedDict, total=False):
    hidden: ReadOnly[bool]
    primary_key: ReadOnly[bool]
    index: ReadOnly[bool]
    default: ReadOnly[object]


class Field[T: FieldArgs](typing.InitField[T]):
    pass


type GetFieldItem[T, K] = typing.GetMemberType[
    typing.GetArg[T, typing.InitField, Literal[0]], K
]


# Strip `| None` from a type by iterating over its union components
# and filtering
type NotOptional[T] = Union[
    *[
        x
        for x in typing.Iter[typing.FromUnion[T]]
        if not typing.IsAssignable[x, None]
    ]
]

# Adjust an attribute type for use in Public below by dropping | None for
# primary keys and stripping all annotations.
type FixPublicType[T, Init] = (
    NotOptional[T]
    if typing.IsAssignable[
        Literal[True], GetFieldItem[Init, Literal["primary_key"]]
    ]
    else T
)

# Strip out everything that is Hidden and also make the primary key required
# Drop all the annotations, since this is for data getting returned to users
# from the DB, so we don't need default values.
type Public[T] = typing.NewProtocol[
    *[
        typing.Member[
            p.name,
            FixPublicType[p.type, p.init],
            p.quals,
        ]
        for p in typing.Iter[typing.Attrs[T]]
        if not typing.IsAssignable[
            Literal[True], GetFieldItem[p.init, Literal["hidden"]]
        ]
    ]
]

# Extract the default type from an Init field.
# If it is a Field, then we try pulling out the "default" field,
# otherwise we return the type itself.
type GetDefault[Init] = (
    GetFieldItem[Init, Literal["default"]]
    if typing.IsAssignable[Init, Field]
    else Init
)

# Create takes everything but the primary key and preserves defaults
type Create[T] = typing.NewProtocol[
    *[
        typing.Member[
            p.name,
            p.type,
            p.quals,
            GetDefault[p.init],
        ]
        for p in typing.Iter[typing.Attrs[T]]
        if not typing.IsAssignable[
            Literal[True],
            GetFieldItem[p.init, Literal["primary_key"]],
        ]
    ]
]

# Update takes everything but the primary key, but makes them all have
# None defaults
type Update[T] = typing.NewProtocol[
    *[
        typing.Member[
            p.name,
            p.type | None,
            p.quals,
            Literal[None],
        ]
        for p in typing.Iter[typing.Attrs[T]]
        if not typing.IsAssignable[
            Literal[True],
            GetFieldItem[p.init, Literal["primary_key"]],
        ]
    ]
]


class Hero:
    id: int | None = Field(default=None, primary_key=True)

    name: str = Field(index=True)
    age: int | None = Field(default=None, index=True)

    secret_name: str = Field(hidden=True)


# Quick reveal_type test for running mypy against this
if TYPE_CHECKING:
    pub_hero: Public[Hero]
    reveal_type(pub_hero)  # noqa

    creat_hero: Create[Hero]
    reveal_type(creat_hero)  # noqa

    upd_hero: Update[Hero]
    reveal_type(upd_hero)  # noqa


if __name__ == '__main__':
    from typemap.type_eval import eval_typing
    from typemap.type_eval import format_helper

    print(format_helper.format_class(eval_typing(Public[Hero])))
    print(format_helper.format_class(eval_typing(Create[Hero])))
    print(format_helper.format_class(eval_typing(Update[Hero])))
