from sqlalchemy.orm import Session

from app.models.conversation import (
    Conversation,
)

from app.models.chat_message import (
    ChatMessage,
)


class MemoryService:


    def create_conversation(

        self,

        db: Session,

        user_id: int,

        provider: str = "groq",

    ) -> Conversation:

        conversation = Conversation(

            user_id=user_id,

            provider=provider,

            title="New conversation",

        )

        db.add(conversation)

        db.commit()

        db.refresh(conversation)

        return conversation


    def get_conversation(

        self,

        db: Session,

        user_id: int,

        conversation_id: int,

    ):

        return (

            db.query(Conversation)

            .filter(

                Conversation.id
                == conversation_id,

                Conversation.user_id
                == user_id,

            )

            .first()

        )

    def delete_conversation(

        self,

        db: Session,

        user_id: int,

        conversation_id: int,

    ) -> bool:

        conversation = (

            self.get_conversation(

                db=db,
                user_id=user_id,

                conversation_id=
                    conversation_id,
            )
        )


        if not conversation:

            return False


        db.delete(conversation)

        db.commit()


        return True

    def list_conversations(

        self,

        db: Session,

        user_id: int,

    ):

        return (

            db.query(Conversation)

            .filter(

                Conversation.user_id
                == user_id

            )

            .order_by(

                Conversation.updated_at.desc()

            )

            .all()

        )


    def add_message(

        self,

        db: Session,

        conversation_id: int,

        role: str,

        content: str,

    ):

        message = ChatMessage(

            conversation_id=
                conversation_id,

            role=role,

            content=content,

        )

        db.add(message)

        db.commit()

        db.refresh(message)

        return message


    def get_history(

        self,

        db: Session,

        conversation_id: int,

        limit: int = 20,

    ):

        messages = (

            db.query(ChatMessage)

            .filter(

                ChatMessage.conversation_id
                == conversation_id

            )

            .order_by(

                ChatMessage.created_at.desc()

            )

            .limit(limit)

            .all()

        )


        messages.reverse()


        return [

            {

                "id": message.id,

                "role": message.role,

                "content": message.content,

                "created_at":
                    message.created_at,

            }

            for message in messages

        ]


    def update_title_from_question(

        self,

        db: Session,

        conversation: Conversation,

        question: str,

    ):

        if (
            conversation.title
            == "New conversation"
        ):

            title = question.strip()

            if len(title) > 50:

                title = (
                    title[:47]
                    + "..."
                )

            conversation.title = title

            db.commit()

            db.refresh(conversation)