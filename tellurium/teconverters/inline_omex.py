from __future__ import print_function, division

import tecombine as libcombine
import phrasedml
import re
import argparse

def saveInlineOMEX(omex_str, out_path):
    '''Saves an inline omex string to a file.

    :param omex_str: The inline omex string
    :type  omex_str: str
    :param out_path: Path to the output file
    :type  out_path: str
    '''
    omex = inlineOmex.fromString(omex_str)
    omex.exportToCombine(out_path)

def parseMagicArgs(line):
    parser = argparse.ArgumentParser()
    parser.add_argument('location')
    parser.add_argument('--master', type=bool)
    return parser.parse_args(line)

class inlineOmex:
    @classmethod
    def fromString(cls, omex_str):
        '''Given mixed Antimony/PhraSEDML, separates out the constituent parts.
        Assumes that Antimony and PhraSEDML are not mixed on the same line.

        :param instr: The input string containing mixed Antimony/PhraSEDML
        :returns: 2-tuple containing a list of Antimony parts and a list of PhraSEDML parts as strings
        '''
        class S_PML:
            # recognizes Antimony start
            sb_start = re.compile(r'^\s*\*?\s*model\s*[^()\s]+\s*(\([^)]*\))?\s*$')
            force_sb_start = re.compile(r'^\s*(%crn|%sb|%antimony|%model).*$')

            def __init__(self, force=False, initl_content='', args=None):
                self.pml = initl_content
                self.force = force
                self.args = args

            def __call__(self, line):
                if self.force_sb_start.match(line) != None:
                    return S_SB(True, args = parseMagicArgs(line.split()[1:])), self.pml if self.force else None, None
                if not self.force and self.sb_start.match(line) != None:
                    return S_SB(self.force, line), self.pml, None
                else:
                    self.pml += line + '\n'
                    return self, None, None

            def dump(self): return self.pml, None

        class S_SB:
            sb_end = re.compile(r'^\s*end\s*$')
            force_pml_start = re.compile(r'^\s*(%tasks|%phrasedml)\s+.*$')

            def __init__(self, force=False, initl_content='', args=None):
                self.sb = initl_content
                self.force = force
                self.args = args

            def __call__(self, line):
                if self.force_pml_start.match(line) != None:
                    return S_PML(True, args = parseMagicArgs(line.split()[1:])), None, self.sb if self.force else None
                if not self.force and self.sb_end.match(line) != None:
                    self.sb += line + '\n'
                    return S_PML(self.force), None, self.sb
                else:
                    self.sb += line + '\n'
                    return self, None, None

            def dump(self): return None, self.sb

        s = S_PML()

        sources = []
        def add_source(src, type):
            if src:
                new_src = {
                    'source': src,
                    'type': type,
                }
                if args is not None:
                    new_src['location'] = args.location
                    if args.master is not None:
                        new_src['master'] = args.master
                    else:
                        new_src['master'] = False
                sources.append(new_src)

        for l in omex_str.splitlines():
            s, pml, sb = s(l)
            args = s.args
            add_source(pml, 'phrasedml')
            add_source(sb,  'antimony')

        pml, sb = s.dump()
        add_source(pml, 'phrasedml')
        add_source(sb,  'antimony')

        # merge phrasedml when no location specified
        if s.force == False:
            phrasedml_combined = ''
            for src in list(sources):
                if src['type'] == 'phrasedml':
                    phrasedml_combined += src['source']
                    sources.remove(src)
            if phrasedml_combined:
                sources.append({
                    'source': phrasedml_combined,
                    'type': 'phrasedml',
                    'location': 'main.xml',
                    'master': True,
                })

        return inlineOmex(sources)

    def __init__(self, sources):
        '''Converts a dictionary of PhraSEDML files and list of Antimony files into sedml/sbml.

        :param sources: Sources returned from partitionInlineOMEXString'''

        from .convert_omex import Omex, SbmlAsset, SedmlAsset
        from .convert_antimony import antimonyConverter

        self.omex = Omex()

        # Convert antimony to sbml
        for t,loc,master in ((x['source'], x['location'] if 'location' in x else None, x['master'] if 'master' in x else None)
            for x in sources if x['type'] == 'antimony'):

            modulename, sbmlstr = antimonyConverter().antimonyToSBML(t)
            self.omex.addSbmlAsset(SbmlAsset(modulename+'.xml', sbmlstr, master=master))

        # Convert phrasedml to sedml
        for t,loc,master in ((x['source'], x['location'] if 'location' in x else None, x['master'] if 'master' in x else None)
            for x in sources if x['type'] == 'phrasedml'):

            for sbml_asset in self.omex.getSbmlAssets():
                phrasedml.setReferencedSBML(sbml_asset.getModuleName(), sbml_asset.getContent())
            phrasedml.convertString(t)
            phrasedml.addDotXMLToModelSources()
            sedml = phrasedml.getLastSEDML()
            if sedml is None:
                raise RuntimeError('Unable to convert PhraSEDML to SED-ML: {}'.format(phrasedml.getLastError()))
            self.omex.addSedmlAsset(SedmlAsset(loc if loc is not None else 'main.xml', sedml, master=master))

    def executeOmex(self):
        self.omex.executeOmex()
