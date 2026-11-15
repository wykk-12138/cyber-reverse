/* entry 6 @ 0x1430e4690 */
const char *__fastcall BrotliDecoderErrorString(int a1)
{
  const char *_ERROR_UNREACHABLE; // rax

  switch ( a1 )
  {
    case -31:
      _ERROR_UNREACHABLE = "_ERROR_UNREACHABLE";
      break;
    case -30:
      _ERROR_UNREACHABLE = "_ERROR_ALLOC_BLOCK_TYPE_TREES";
      break;
    case -27:
      _ERROR_UNREACHABLE = "_ERROR_ALLOC_RING_BUFFER_2";
      break;
    case -26:
      _ERROR_UNREACHABLE = "_ERROR_ALLOC_RING_BUFFER_1";
      break;
    case -25:
      _ERROR_UNREACHABLE = "_ERROR_ALLOC_CONTEXT_MAP";
      break;
    case -22:
      _ERROR_UNREACHABLE = "_ERROR_ALLOC_TREE_GROUPS";
      break;
    case -21:
      _ERROR_UNREACHABLE = "_ERROR_ALLOC_CONTEXT_MODES";
      break;
    case -20:
      _ERROR_UNREACHABLE = "_ERROR_INVALID_ARGUMENTS";
      break;
    case -19:
      _ERROR_UNREACHABLE = "_ERROR_DICTIONARY_NOT_SET";
      break;
    case -18:
      _ERROR_UNREACHABLE = "_ERROR_COMPOUND_DICTIONARY";
      break;
    case -16:
      _ERROR_UNREACHABLE = "_ERROR_FORMAT_DISTANCE";
      break;
    case -15:
      _ERROR_UNREACHABLE = "_ERROR_FORMAT_PADDING_2";
      break;
    case -14:
      _ERROR_UNREACHABLE = "_ERROR_FORMAT_PADDING_1";
      break;
    case -13:
      _ERROR_UNREACHABLE = "_ERROR_FORMAT_WINDOW_BITS";
      break;
    case -12:
      _ERROR_UNREACHABLE = "_ERROR_FORMAT_DICTIONARY";
      break;
    case -11:
      _ERROR_UNREACHABLE = "_ERROR_FORMAT_TRANSFORM";
      break;
    case -10:
      _ERROR_UNREACHABLE = "_ERROR_FORMAT_BLOCK_LENGTH_2";
      break;
    case -9:
      _ERROR_UNREACHABLE = "_ERROR_FORMAT_BLOCK_LENGTH_1";
      break;
    case -8:
      _ERROR_UNREACHABLE = "_ERROR_FORMAT_CONTEXT_MAP_REPEAT";
      break;
    case -7:
      _ERROR_UNREACHABLE = "_ERROR_FORMAT_HUFFMAN_SPACE";
      break;
    case -6:
      _ERROR_UNREACHABLE = "_ERROR_FORMAT_CL_SPACE";
      break;
    case -5:
      _ERROR_UNREACHABLE = "_ERROR_FORMAT_SIMPLE_HUFFMAN_SAME";
      break;
    case -4:
      _ERROR_UNREACHABLE = "_ERROR_FORMAT_SIMPLE_HUFFMAN_ALPHABET";
      break;
    case -3:
      _ERROR_UNREACHABLE = "_ERROR_FORMAT_EXUBERANT_META_NIBBLE";
      break;
    case -2:
      _ERROR_UNREACHABLE = "_ERROR_FORMAT_RESERVED";
      break;
    case -1:
      _ERROR_UNREACHABLE = "_ERROR_FORMAT_EXUBERANT_NIBBLE";
      break;
    case 0:
      _ERROR_UNREACHABLE = "_NO_ERROR";
      break;
    case 1:
      _ERROR_UNREACHABLE = "_SUCCESS";
      break;
    case 2:
      _ERROR_UNREACHABLE = "_NEEDS_MORE_INPUT";
      break;
    case 3:
      _ERROR_UNREACHABLE = "_NEEDS_MORE_OUTPUT";
      break;
    default:
      _ERROR_UNREACHABLE = "INVALID";
      break;
  }
  return _ERROR_UNREACHABLE;
}
