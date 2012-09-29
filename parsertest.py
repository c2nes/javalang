
import sys

import java

def parse_file(filename, debug):
    code = open(filename).read()
    tokens = java.tokenizer.tokenize(code)
    parser = java.parser.Parser(tokens)
    parser.set_debug(debug)

    try:
        return parser.parse()
    except java.parser.JavaSyntaxError as e:
        sys.stderr.write('Error in {0}\n'.format(filename))
        sys.stderr.write(e.description + '\n')
        if e.at.position:
            sys.stderr.write("    at '{0}' line {1[0]}, character {1[1]}\n".format(
                    e.at.value, e.at.position))
        sys.stderr.write('\n')

    except java.tokenizer.LexerError as e:
        sys.stderr.write('Error in {0}\n'.format(filename))
        sys.stderr.write(unicode(e) + '\n\n')

    except Exception:
        print filename
        print parser.tokens.look()
        raise

def dump(ast):
    for path, node in ast:
        path = "->".join(["{0[0]}[{0[1]}]".format(p) for p in path])
        node = {attr : getattr(node, attr) for attr in node.attrs if isinstance(getattr(node, attr), (set, basestring))}
        print path, node

def process(args):
    import os
    import time

    paths = args.paths
    walk = args.walk
    debug = args.debug

    files_processed = list()
    start_time = time.time()

    for path in paths:
        if path.endswith('.java'):
            files_processed.append(path)
            ast = parse_file(path, debug)

            if not ast:
                sys.exit(1)

            if walk:
                dump(ast)
        else:
            for dirpath, _, filenames in os.walk(path):
                filenames = [f for f in filenames if f.endswith('.java')]

                for filename in filenames:
                    source_file = os.path.join(dirpath, filename)
                    ast = parse_file(source_file, debug)

                    if not ast:
                        sys.exit(1)

                    if walk:
                        dump(ast)

                    files_processed.append(source_file)

    total_time = time.time() - start_time
    print "Processed {0} files in {1:.6f} seconds".format(len(files_processed), total_time)

def main():
    import argparse

    parser = argparse.ArgumentParser(prog='parsertest', description='Java parser test interface')
    parser.add_argument('-d', '--debug', default=False, const=True,
                        action='store_const', help='enable debugging')
    parser.add_argument('--profile', default=False, const=True,
                        action='store_const', help='enable profiling')
    parser.add_argument('--walk', default=False, const=True,
                        action='store_const', help='print AST after parsing')
    parser.add_argument('paths', metavar='path', nargs='+',
                        help='directory or file to process')
    args = parser.parse_args()

    if args.profile:
        import cProfile as profile
        import pstats
        profile.runctx('process(args)', globals(), locals(), 'prof.txt')
        stats = pstats.Stats('prof.txt')
        stats.sort_stats('time')
        stats.print_stats()
    else:
        process(args)

if __name__ == '__main__':
    main()
