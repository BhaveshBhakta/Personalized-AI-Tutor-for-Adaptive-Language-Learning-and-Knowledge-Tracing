from app.db.base_class import Base

from app.models.user import User
from app.models.learning_profile import LearningProfile
from app.models.vocabulary import Vocabulary
from app.models.flashcard import Flashcard
from app.models.german_word import GermanWord
from app.models.grammar_topic import GrammarTopic
from app.models.grammar_progress import GrammarProgress
from app.models.grammar_question import GrammarQuestion
from app.models.document import Document
from app.models.document_chunk import DocumentChunk
from app.models.conversation import Conversation
from app.models.chat_message import ChatMessage
from app.models.learning_signal import LearningSignal
from app.models.adaptive_exercise import (AdaptiveExercise,)
from app.models.exercise_attempt import (ExerciseAttempt,)