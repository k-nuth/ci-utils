#
# Copyright (c) 2017-2018 Bitprim Inc.
#
# This file is part of Bitprim.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#

# import os
# from utils import get_cpu_microarchitecture, get_cpuid
import copy
import difflib

marchs_extensions = {
    'x86-64':         ['64-bit extensions'],
# Intel
    #tock
    'core2':          ['64-bit extensions', 'MMX', 'SSE', 'SSE2', 'SSE3', 'SSSE3'],
    #tick
    # 'penryn':         ['64-bit extensions', 'MMX', 'SSE', 'SSE2', 'SSE3', 'SSSE3', 'SSE4', 'SSE4.1'],
    #tock
    'nehalem':        ['64-bit extensions', 'MMX', 'SSE', 'SSE2', 'SSE3', 'SSSE3', 'SSE4', 'SSE4.1', 'SSE4.2', 'POPCNT'],
    #tick
    'westmere':       ['64-bit extensions', 'MMX', 'SSE', 'SSE2', 'SSE3', 'SSSE3', 'SSE4', 'SSE4.1', 'SSE4.2', 'POPCNT', 'AES', 'PCLMUL'],
    #tock
    'sandybridge':    ['64-bit extensions', 'MMX', 'SSE', 'SSE2', 'SSE3', 'SSSE3', 'SSE4', 'SSE4.1', 'SSE4.2', 'POPCNT', 'AES', 'PCLMUL', 'AVX'],
    #tick
    'ivybridge':      ['64-bit extensions', 'MMX', 'SSE', 'SSE2', 'SSE3', 'SSSE3', 'SSE4', 'SSE4.1', 'SSE4.2', 'POPCNT', 'AES', 'PCLMUL', 'AVX', 'FSGSBASE', 'RDRND', 'F16C'],
    #tock
    'haswell':        ['64-bit extensions', 'MMX', 'SSE', 'SSE2', 'SSE3', 'SSSE3', 'SSE4', 'SSE4.1', 'SSE4.2', 'POPCNT', 'AES', 'PCLMUL', 'AVX', 'FSGSBASE', 'RDRND', 'F16C', 'FMA', 'BMI', 'BMI2', 'MOVBE', 'AVX2'],
    #tick/process
    'broadwell':      ['64-bit extensions', 'MMX', 'SSE', 'SSE2', 'SSE3', 'SSSE3', 'SSE4', 'SSE4.1', 'SSE4.2', 'POPCNT', 'AES', 'PCLMUL', 'AVX', 'FSGSBASE', 'RDRND', 'F16C', 'FMA', 'BMI', 'BMI2', 'MOVBE', 'AVX2', 'RDSEED', 'ADCX', 'PREFETCHW'],  #TXT, TSX, 
                                 

    'skylake':        ['64-bit extensions', 'MMX', 'SSE', 'SSE2', 'SSE3', 'SSSE3', 'SSE4', 'SSE4.1', 'SSE4.2', 'POPCNT', 'AES', 'PCLMUL', 'AVX', 'FSGSBASE', 'RDRND', 'F16C', 'FMA', 'BMI', 'BMI2', 'MOVBE', 'AVX2', 'RDSEED', 'ADCX', 'PREFETCHW', 'CLFLUSHOPT', 'XSAVEC', 'XSAVES'],
    'skylake-avx512': ['64-bit extensions', 'MMX', 'SSE', 'SSE2', 'SSE3', 'SSSE3', 'SSE4', 'SSE4.1', 'SSE4.2', 'POPCNT', 'AES', 'PCLMUL', 'AVX', 'FSGSBASE', 'RDRND', 'F16C', 'FMA', 'BMI', 'BMI2', 'MOVBE', 'AVX2', 'RDSEED', 'ADCX', 'PREFETCHW', 'CLFLUSHOPT', 'XSAVEC', 'XSAVES', 'AVX512F', 'AVX512CD', 'AVX512VL', 'AVX512BW', 'AVX512DQ', 'PKU', 'CLWB'],
    # Kaby Lake
    # Coffee Lake
    # Whiskey Lake
    # Cascade Lake
    'cannonlake':     ['64-bit extensions', 'MMX', 'SSE', 'SSE2', 'SSE3', 'SSSE3', 'SSE4', 'SSE4.1', 'SSE4.2', 'POPCNT', 'AES', 'PCLMUL', 'AVX', 'FSGSBASE', 'RDRND', 'F16C', 'FMA', 'BMI', 'BMI2', 'MOVBE', 'AVX2', 'RDSEED', 'ADCX', 'PREFETCHW', 'CLFLUSHOPT', 'XSAVEC', 'XSAVES', 'AVX512F', 'AVX512CD', 'AVX512VL', 'AVX512BW', 'AVX512DQ', 'PKU', '????', 'AVX512VBMI', 'AVX512IFMA', 'SHA', 'UMIP'],
    'icelake-client': ['64-bit extensions', 'MMX', 'SSE', 'SSE2', 'SSE3', 'SSSE3', 'SSE4', 'SSE4.1', 'SSE4.2', 'POPCNT', 'AES', 'PCLMUL', 'AVX', 'FSGSBASE', 'RDRND', 'F16C', 'FMA', 'BMI', 'BMI2', 'MOVBE', 'AVX2', 'RDSEED', 'ADCX', 'PREFETCHW', 'CLFLUSHOPT', 'XSAVEC', 'XSAVES', 'AVX512F', 'AVX512CD', 'AVX512VL', 'AVX512BW', 'AVX512DQ', 'PKU', 'CLWB', 'AVX512VBMI', 'AVX512IFMA', 'SHA', 'UMIP', 'RDPID', 'GFNI', 'AVX512VBMI2', 'AVX512VPOPCNTDQ', 'AVX512BITALG', 'AVX512VNNI', 'VPCLMULQDQ', 'VAES'],
    'icelake-server': ['64-bit extensions', 'MMX', 'SSE', 'SSE2', 'SSE3', 'SSSE3', 'SSE4', 'SSE4.1', 'SSE4.2', 'POPCNT', 'AES', 'PCLMUL', 'AVX', 'FSGSBASE', 'RDRND', 'F16C', 'FMA', 'BMI', 'BMI2', 'MOVBE', 'AVX2', 'RDSEED', 'ADCX', 'PREFETCHW', 'CLFLUSHOPT', 'XSAVEC', 'XSAVES', 'AVX512F', 'AVX512CD', 'AVX512VL', 'AVX512BW', 'AVX512DQ', 'PKU', 'CLWB', 'AVX512VBMI', 'AVX512IFMA', 'SHA', 'UMIP', 'RDPID', 'GFNI', 'AVX512VBMI2', 'AVX512VPOPCNTDQ', 'AVX512BITALG', 'AVX512VNNI', 'VPCLMULQDQ', 'VAES', 'PCONFIG', 'WBNOINVD'],
    # Tiger Lake
    # Sapphire Rapids

# Intel Atom
    'bonnell':        ['64-bit extensions', 'MMX', 'SSE', 'SSE2', 'SSE3', 'SSSE3', 'MOVBE'],
    'silvermont':     ['64-bit extensions', 'MMX', 'SSE', 'SSE2', 'SSE3', 'SSSE3', 'MOVBE', 'SSE4', 'SSE4.1', 'SSE4.2', 'POPCNT', 'AES', 'PCLMUL', 'RDRND'],
    'goldmont':       ['64-bit extensions', 'MMX', 'SSE', 'SSE2', 'SSE3', 'SSSE3', 'MOVBE', 'SSE4', 'SSE4.1', 'SSE4.2', 'POPCNT', 'AES', 'PCLMUL', 'RDRND', 'XSAVE', 'XSAVEOPT', 'FSGSBASE'],
    'goldmont-plus':  ['64-bit extensions', 'MMX', 'SSE', 'SSE2', 'SSE3', 'SSSE3', 'MOVBE', 'SSE4', 'SSE4.1', 'SSE4.2', 'POPCNT', 'AES', 'PCLMUL', 'RDRND', 'XSAVE', 'XSAVEOPT', 'FSGSBASE', 'PTWRITE', 'RDPID', 'SGX', 'UMIP'],
    'tremont':        ['64-bit extensions', 'MMX', 'SSE', 'SSE2', 'SSE3', 'SSSE3', 'MOVBE', 'SSE4', 'SSE4.1', 'SSE4.2', 'POPCNT', 'AES', 'PCLMUL', 'RDRND', 'XSAVE', 'XSAVEOPT', 'FSGSBASE', 'PTWRITE', 'RDPID', 'SGX', 'UMIP', 'GFNI-SSE', 'CLWB', 'ENCLV'],

#????
    'knl':            ['64-bit extensions', 'MMX', 'SSE', 'SSE2', 'SSE3', 'SSSE3', 'SSE4', 'SSE4.1', 'SSE4.2', 'POPCNT', 'AES', 'PCLMUL', 'AVX', 'FSGSBASE', 'RDRND', 'F16C', 'FMA', 'BMI', 'BMI2', 'MOVBE', 'AVX2', 'RDSEED', 'ADCX', 'PREFETCHW',                                   'AVX512F', 'AVX512CD', 'AVX512PF', 'AVX512ER'],
    'knm':            ['64-bit extensions', 'MMX', 'SSE', 'SSE2', 'SSE3', 'SSSE3', 'SSE4', 'SSE4.1', 'SSE4.2', 'POPCNT', 'AES', 'PCLMUL', 'AVX', 'FSGSBASE', 'RDRND', 'F16C', 'FMA', 'BMI', 'BMI2', 'MOVBE', 'AVX2', 'RDSEED', 'ADCX', 'PREFETCHW',                                   'AVX512F', 'AVX512CD', 'AVX512PF', 'AVX512ER', 'AVX5124VNNIW', 'AVX5124FMAPS', 'AVX512VPOPCNTDQ'],



# AMD       https://en.wikipedia.org/wiki/List_of_AMD_CPU_microarchitectures
#           AMD K8 Hammer: k8, opteron, athlon64, athlon-fx
#           https://en.wikipedia.org/wiki/AMD_K8
    'k8':            ['64-bit extensions', 'MMX', 'SSE', 'SSE2', '3DNow!', 'enhanced 3DNow!'],
    'opteron':       ['64-bit extensions', 'MMX', 'SSE', 'SSE2', '3DNow!', 'enhanced 3DNow!'],
    'athlon64':      ['64-bit extensions', 'MMX', 'SSE', 'SSE2', '3DNow!', 'enhanced 3DNow!'],
    'athlon-fx':     ['64-bit extensions', 'MMX', 'SSE', 'SSE2', '3DNow!', 'enhanced 3DNow!'],

#           AMD K8 Hammer with SSE3: k8-sse3, opteron-sse3, athlon64-sse3
    'k8-sse3':       ['64-bit extensions', 'MMX', 'SSE', 'SSE2', '3DNow!', 'enhanced 3DNow!', 'SSE3'],
    'opteron-sse3':  ['64-bit extensions', 'MMX', 'SSE', 'SSE2', '3DNow!', 'enhanced 3DNow!', 'SSE3'],
    'athlon64-sse3': ['64-bit extensions', 'MMX', 'SSE', 'SSE2', '3DNow!', 'enhanced 3DNow!', 'SSE3'],

#           AMD Family 10h, or K10: amdfam10, barcelona            
#           https://en.wikipedia.org/wiki/AMD_10h
    'amdfam10':      ['64-bit extensions', 'MMX', 'SSE', 'SSE2', '3DNow!', 'enhanced 3DNow!', 'SSE3', 'SSE4A', 'ABM'],
    'barcelona':     ['64-bit extensions', 'MMX', 'SSE', 'SSE2', '3DNow!', 'enhanced 3DNow!', 'SSE3', 'SSE4A', 'ABM'],

#           AMD Bobcat Family 14h (low-power/low-cost market)   https://en.wikipedia.org/wiki/Bobcat_(microarchitecture)
    'btver1':        ['64-bit extensions', 'MMX', 'SSE', 'SSE2', '3DNow!', 'enhanced 3DNow!', 'SSE3', 'SSE4A', 'ABM', 'SSSE3', 'CX16'],
#           AMD Jaguar Family 16h (low-power/low-cost market)   https://en.wikipedia.org/wiki/Jaguar_(microarchitecture)
    'btver2':        ['64-bit extensions', 'MMX', 'SSE', 'SSE2', '3DNow!', 'enhanced 3DNow!', 'SSE3', 'SSE4A', 'ABM', 'SSSE3', 'CX16', 'MOVBE', 'F16C', 'BMI', 'AVX', 'PCL_MUL', 'AES', 'SSE4.2', 'SSE4.1'],
#           AMD Puma Family 16h (2nd-gen) (low-power/low-cost market)   https://en.wikipedia.org/wiki/Puma_(microarchitecture)
#           ????

#           AMD Bulldozer Family 15h (1st-gen)      https://en.wikipedia.org/wiki/Bulldozer_(microarchitecture)
    'bdver1':        ['64-bit extensions', 'MMX', 'SSE', 'SSE2', '3DNow!', 'enhanced 3DNow!', 'SSE3', 'SSE4A', 'ABM', 'SSSE3', 'SSE4.1', 'SSE4.2', 'FMA4', 'AVX', 'XOP', 'LWP', 'AES', 'PCL_MUL', 'CX16'],
#           AMD Piledriver Family 15h (2nd-gen)     https://en.wikipedia.org/wiki/Piledriver_(microarchitecture)
    'bdver2':        ['64-bit extensions', 'MMX', 'SSE', 'SSE2', '3DNow!', 'enhanced 3DNow!', 'SSE3', 'SSE4A', 'ABM', 'SSSE3', 'SSE4.1', 'SSE4.2', 'FMA4', 'AVX', 'XOP', 'LWP', 'AES', 'PCL_MUL', 'CX16', 'BMI', 'TBM', 'F16C', 'FMA'],
#           AMD Steamroller Family 15h (3rd-gen)    https://en.wikipedia.org/wiki/Steamroller_(microarchitecture)
    'bdver3':        ['64-bit extensions', 'MMX', 'SSE', 'SSE2', '3DNow!', 'enhanced 3DNow!', 'SSE3', 'SSE4A', 'ABM', 'SSSE3', 'SSE4.1', 'SSE4.2', 'FMA4', 'AVX', 'XOP', 'LWP', 'AES', 'PCL_MUL', 'CX16', 'BMI', 'TBM', 'F16C', 'FMA', 'FSGSBASE'],
#           AMD Excavator Family 15h (4th-gen)      https://en.wikipedia.org/wiki/Excavator_(microarchitecture)
    'bdver4':        ['64-bit extensions', 'MMX', 'SSE', 'SSE2', '3DNow!', 'enhanced 3DNow!', 'SSE3', 'SSE4A', 'ABM', 'SSSE3', 'SSE4.1', 'SSE4.2', 'FMA4', 'AVX', 'XOP', 'LWP', 'AES', 'PCL_MUL', 'CX16', 'BMI', 'TBM', 'F16C', 'FMA', 'FSGSBASE', 'AVX2', 'BMI2', 'MOVBE'],
#           AMD Zen                                 https://en.wikipedia.org/wiki/Zen_(microarchitecture)
    'znver1':        ['64-bit extensions', 'MMX', 'SSE', 'SSE2', '3DNow!', 'enhanced 3DNow!', 'SSE3', 'SSE4A', 'ABM', 'SSSE3', 'SSE4.1', 'SSE4.2', 'FMA4', 'AVX', 'XOP', 'LWP', 'AES', 'PCL_MUL', 'CX16', 'BMI', 'TBM', 'F16C', 'FMA', 'FSGSBASE', 'AVX2', 'BMI2', 'MOVBE', 'ADCX', 'RDSEED', 'MWAITX', 'SHA', 'CLZERO', 'XSAVEC', 'XSAVES', 'CLFLUSHOPT', 'POPCNT'],

# VIA
    'eden-x2':        ['64-bit extensions', 'MMX', 'SSE', 'SSE2', 'SSE3'],
    'eden-x4':        ['64-bit extensions', 'MMX', 'SSE', 'SSE2', 'SSE3', 'SSSE3', 'SSE4.1', 'SSE4.2', 'AVX', 'AVX2'],

    'nano':           ['64-bit extensions', 'MMX', 'SSE', 'SSE2', 'SSE3', 'SSSE3'],
    'nano-1000':      ['64-bit extensions', 'MMX', 'SSE', 'SSE2', 'SSE3', 'SSSE3'], 
    'nano-2000':      ['64-bit extensions', 'MMX', 'SSE', 'SSE2', 'SSE3', 'SSSE3'], 
    'nano-3000':      ['64-bit extensions', 'MMX', 'SSE', 'SSE2', 'SSE3', 'SSSE3', 'SSE4.1'], 
    'nano-x2':        ['64-bit extensions', 'MMX', 'SSE', 'SSE2', 'SSE3', 'SSSE3', 'SSE4.1'], 
    'nano-x4':        ['64-bit extensions', 'MMX', 'SSE', 'SSE2', 'SSE3', 'SSSE3', 'SSE4.1'], 

}

marchs_aliases = {
    'k8':            'k8',
    'opteron':       'k8',
    'athlon64':      'k8',
    'athlon-fx':     'k8',
    'k8-sse3':       'k8-sse3',
    'opteron-sse3':  'k8-sse3',
    'athlon64-sse3': 'k8-sse3',
    'k10':           'amdfam10',
    'amdfam10':      'amdfam10',
    'barcelona':     'amdfam10',
    'bobcat':        'btver1',
    'jaguar':        'btver2',
    # 'puma':          'btver2',
    # 'leopard':       'btver3',
    # 'margay':        'btver4',
    'bulldozer':      'bdver1',
    'piledriver':     'bdver2',
    'steamroller':    'bdver3',
    'excavator':      'bdver4',

    'knightslanding': 'knl',
    'atom':           'bonnell',
    'kabylake':       'skylake',
}

def remove_ext(data, ext):
    for _, value in data.items():
        if ext in value:
            value.remove(ext)


marchs_families = {}
marchs_families['gcc']= {}
marchs_families['apple-clang']= {}
marchs_families['clang']= {}
marchs_families['msvc']= {}
marchs_families['mingw']= {}

# msvc 2017
    # (x86)
        # /arch:[IA32|SSE|SSE2|AVX|AVX2]  
    # (x64)
        # /arch:[AVX|AVX2]  
    # (ARM)
        # /arch:[ARMv7VE|VFPv4]  

marchs_families['msvc'][14] = {
    'amd_high':   ['x86-64', 'bdver1', 'bdver4'],
    'amd_low':    ['x86-64', 'btver2'],
    'intel_core': ['x86-64', 'sandybridge', 'haswell'],
    'via_eden':   ['x86-64', 'eden-x4'],
}

marchs_families['msvc'][15] = copy.deepcopy(marchs_families['msvc'][14])


msvc_to_extensions = {
    'x86-64':        None,
    'bdver1':       'AVX',
    'bdver4':       'AVX2',
    'btver2':       'AVX',
    'sandybridge':  'AVX',
    'haswell':      'AVX2',
    'eden-x4':      'AVX2',
}

def msvc_to_ext(march):
    if march in msvc_to_extensions:
        msvc_to_extensions[march]
    
    return None

marchs_families_base = {
    'amd_high':   ['x86-64', 'k8', 'k8-sse3', 'amdfam10', 'bdver1', 'bdver2', 'bdver3', 'bdver4'],
    'amd_low':    ['x86-64', 'k8', 'k8-sse3', 'amdfam10', 'btver1', 'btver2'],
    # 'intel_core': ['x86-64', 'core2', 'penryn', 'nehalem', 'westmere', 'sandybridge', 'ivybridge', 'haswell', 'broadwell'],
    'intel_core': ['x86-64', 'core2', 'nehalem', 'westmere', 'sandybridge', 'ivybridge', 'haswell', 'broadwell'],
    'intel_atom': ['x86-64', 'core2', 'bonnell', 'silvermont'],
}



marchs_families_clang_base = copy.deepcopy(marchs_families_base)
marchs_families_clang_base['intel_high'] = copy.deepcopy(marchs_families_clang_base['intel_core'])
marchs_families_clang_base['intel_core'].extend(['skylake', 'skylake-avx512', 'cannonlake'])
marchs_families_clang_base['intel_high'].extend(['knl'])

marchs_families['clang'][4.0] = copy.deepcopy(marchs_families_clang_base)
marchs_families['clang'][4.0]['amd_high'].extend(['znver1'])

marchs_families['apple-clang'][9.1] = copy.deepcopy(marchs_families['clang'][4.0])
marchs_families['apple-clang'][9.1]['intel_atom'].extend(['goldmont'])

marchs_families['gcc'][4] = copy.deepcopy(marchs_families_base)

marchs_families['gcc'][5] = copy.deepcopy(marchs_families['gcc'][4])
marchs_families['gcc'][5]['intel_high'] = copy.deepcopy(marchs_families['gcc'][5]['intel_core'])
marchs_families['gcc'][5]['intel_high'].extend(['knl'])

marchs_families['mingw'][7] = copy.deepcopy(marchs_families['gcc'][5])
marchs_families['mingw'][7]['intel_core'].extend(['skylake'])
marchs_families['mingw'][7]['amd_high'].extend(['znver1'])

marchs_families['gcc'][6] = copy.deepcopy(marchs_families['mingw'][7])
marchs_families['gcc'][6]['intel_core'].extend(['skylake-avx512'])

marchs_families['mingw'][6] = copy.deepcopy(marchs_families['gcc'][6])
remove_ext(marchs_families['mingw'][6], "skylake-avx512")

marchs_families['mingw'][5] = copy.deepcopy(marchs_families['gcc'][5])

marchs_families['gcc'][7] = copy.deepcopy(marchs_families['gcc'][6])
marchs_families['gcc'][7]['via_eden'] = ['x86-64', 'eden-x2', 'eden-x4']
marchs_families['gcc'][7]['via_nano'] = ['x86-64', 'nano', 'nano-1000', 'nano-2000', 'nano-3000', 'nano-x2', 'nano-x4']

marchs_families['gcc'][8] = copy.deepcopy(marchs_families['gcc'][7])
marchs_families['gcc'][8]['intel_high'].extend(['knm'])
marchs_families['gcc'][8]['intel_core'].extend(['cannonlake', 'icelake-client', 'icelake-server'])

marchs_families['mingw'][8] = copy.deepcopy(marchs_families['gcc'][7])
marchs_families['mingw'][8]['intel_high'].extend(['knm'])
remove_ext(marchs_families['mingw'][8], "skylake-avx512")


marchs_families['gcc'][9] = copy.deepcopy(marchs_families['gcc'][8])
marchs_families['gcc'][9]['intel_atom'].extend(['goldmont', 'goldmont-plus', 'tremont'])

# marchs_families['clang'][6.0] = copy.deepcopy(marchs_families['gcc'][9])
# marchs_families['clang'][5.0] = copy.deepcopy(marchs_families['gcc'][9])
# marchs_families['clang'][4.0] = copy.deepcopy(marchs_families['gcc'][9])
marchs_families['clang'][6.0] = copy.deepcopy(marchs_families['apple-clang'][9.1])
marchs_families['clang'][5.0] = copy.deepcopy(marchs_families['apple-clang'][9.1])
# marchs_families['clang'][4.0] = copy.deepcopy(marchs_families['apple-clang'][9.1])

marchs_families['apple-clang'][9.0] = copy.deepcopy(marchs_families['apple-clang'][9.1])
marchs_families['apple-clang'][8.3] = copy.deepcopy(marchs_families_clang_base)
marchs_families['apple-clang'][8.1] = copy.deepcopy(marchs_families_clang_base)
marchs_families['apple-clang'][7.3] = copy.deepcopy(marchs_families_clang_base)
remove_ext(marchs_families['apple-clang'][7.3], "skylake")
remove_ext(marchs_families['apple-clang'][7.3], "cannonlake")
remove_ext(marchs_families['apple-clang'][7.3], "skylake-avx512")


def get_full_family():
    return marchs_families['gcc'][9]

def translate_alias(alias):
    if alias in marchs_aliases:
        return marchs_aliases[alias]
    else:
        return alias

def adjust_compiler_name(os, compiler):
    if os == "Windows" and compiler == "gcc":
        return "mingw"
    if compiler == "Visual Studio":
        return "msvc"
        
    return compiler
        
def get_march_basis(march_detected, os, compiler, compiler_version, full, default):
    compiler = adjust_compiler_name(os, compiler)

    if compiler not in marchs_families:
        return default

    if compiler_version not in marchs_families[compiler]:
        return default

    data = marchs_families[compiler][compiler_version]
    march_detected = translate_alias(march_detected)

    for key, value in data.items():
        if march_detected in value:
            return march_detected
        else:
            if march_detected in full[key]:
                idx = full[key].index(march_detected)
                idx = min(idx, len(value) - 1)
                return value[idx]

    return default

def get_march(march_detected, os, compiler, compiler_version):
    full = get_full_family()
    default = 'x86-64'
    return get_march_basis(march_detected, os, compiler, compiler_version, full, default)

def march_exists_in(march_detected, os, compiler, compiler_version):
    compiler = adjust_compiler_name(os, compiler)

    if compiler not in marchs_families:
        return False

    if compiler_version not in marchs_families[compiler]:
        return False

    data = marchs_families[compiler][compiler_version]
    march_detected = translate_alias(march_detected)

    for _, value in data.items():
        if march_detected in value:
            return True

    return False

def march_exists_full(march_detected):
    data = get_full_family()
    march_detected = translate_alias(march_detected)

    for _, value in data.items():
        if march_detected in value:
            return True

    return False

def marchs_full_list_basis(data):
    ret = []
    for _, value in data.items():
        ret.extend(value)
    return list(set(ret))

def marchs_full_list():
    full = get_full_family()
    return marchs_full_list_basis(full)

def marchs_compiler_list(os, compiler, compiler_version):
    compiler = adjust_compiler_name(os, compiler)

    if compiler not in marchs_families:
        return []

    if compiler_version not in marchs_families[compiler]:
        return []

    data = marchs_families[compiler][compiler_version]
    return marchs_full_list_basis(data)

def filter_valid_exts(os, compiler, compiler_version, list):
    data = marchs_compiler_list(os, compiler, compiler_version)

    ret = []
    for x in list:
        if x in data:
            ret.extend(x)
    return list(set(ret))

def march_close_name(march_incorrect): #, compiler, compiler_version):
    # full = get_full_family()
    return difflib.get_close_matches(march_incorrect, marchs_full_list())
    


# >>> difflib.get_close_matches('anlmal', ['car', 'animal', 'house', 'animation'])

# --------------------------------------------------------------------------------

# def print_extensions():
#     ma = get_cpu_microarchitecture()
#     print(ma)
#     print(marchs_extensions[ma])

# print_extensions()
# print( get_march('broadwell', 'gcc', 4) )
# print( get_march('skylake', 'gcc', 4) )
# print( get_march('skylake-avx512', 'gcc', 4) )

# print( get_march('broadwell', 'gcc', 5) )
# print( get_march('skylake', 'gcc', 5) )
# print( get_march('skylake-avx512', 'gcc', 5) )

# print( get_march('broadwell', 'gcc', 6) )
# print( get_march('skylake', 'gcc', 6) )
# print( get_march('skylake-avx512', 'gcc', 6) )

# print( get_march('broadwell', 'gcc', 7) )
# print( get_march('skylake', 'gcc', 7) )
# print( get_march('skylake-avx512', 'gcc', 7) )

# print( get_march('broadwell', 'gcc', 8) )
# print( get_march('skylake', 'gcc', 8) )
# print( get_march('skylake-avx512', 'gcc', 8) )

# print( get_march('knightslanding', 'gcc', 8) )
# print( get_march('excavator', 'gcc', 8) )
# print( get_march('bdver4', 'gcc', 8) )



# --------------------------------------------------------------------------------

# marchs_families_apple91_temp = {
#     'amd_high':   ['x86-64', 'k8', 'k8-sse3', 'amdfam10', 'bdver1', 'bdver2', 'bdver3', 'bdver4', 'znver1'],
#     'amd_low':    ['x86-64', 'k8', 'k8-sse3', 'amdfam10', 'btver1', 'btver2'],

#     'intel_core': ['x86-64', 'core2', 'nehalem', 'westmere', 'sandybridge', 'ivybridge', 'haswell', 'broadwell', 'skylake', 'skylake-avx512', 'cannonlake'],
#     'intel_atom': ['x86-64', 'core2', 'bonnell', 'silvermont', 'goldmont'],
#     'intel_high': ['x86-64', 'core2', 'nehalem', 'westmere', 'sandybridge', 'ivybridge', 'haswell', 'broadwell', 'knl'],
# }

# marchs_families_gcc4_temp = {
#     'amd_high':   ['x86-64', 'k8', 'k8-sse3', 'amdfam10', 'bdver1', 'bdver2', 'bdver3', 'bdver4'],
#     'amd_low':    ['x86-64', 'k8', 'k8-sse3', 'amdfam10', 'btver1', 'btver2'],

#     'intel_core': ['x86-64', 'core2', 'nehalem', 'westmere', 'sandybridge', 'ivybridge', 'haswell', 'broadwell'],
#     'intel_atom': ['x86-64', 'core2', 'bonnell', 'silvermont'],
#     # 'intel_high': ['x86-64', 'core2', 'nehalem', 'westmere', 'sandybridge', 'ivybridge', 'haswell', 'broadwell'],
# }


# marchs_families_gcc8_temp = {
#     'amd_high':   ['x86-64', 'k8', 'k8-sse3', 'amdfam10', 'bdver1', 'bdver2', 'bdver3', 'bdver4', 'znver1'],
#     'amd_low':    ['x86-64', 'k8', 'k8-sse3', 'amdfam10', 'btver1', 'btver2'],

#     'intel_core': ['x86-64', 'core2', 'nehalem', 'westmere', 'sandybridge', 'ivybridge', 'haswell', 'broadwell', 'skylake', 'skylake-avx512', 'cannonlake', 'icelake-client', 'icelake-server'],
#     'intel_atom': ['x86-64', 'core2', 'bonnell', 'silvermont'],
#     'intel_high': ['x86-64', 'core2', 'nehalem', 'westmere', 'sandybridge', 'ivybridge', 'haswell', 'broadwell', 'knl', 'knm'],

#     'via_eden':   ['x86-64', 'eden-x2', 'eden-x4'],
#     'via_nano':   ['x86-64', 'nano', 'nano-1000', 'nano-2000', 'nano-3000', 'nano-x2', 'nano-x4'],
# }


# print(marchs_families['gcc'][4])
# print()
# print(marchs_families['gcc'][5])
# print()
# print(marchs_families['gcc'][6])
# print()
# print(marchs_families['gcc'][7])
# print()
# print(marchs_families['gcc'][8])

# print(marchs_families['gcc'][4] == marchs_families_gcc4_temp)
# print(marchs_families['gcc'][8] == marchs_families_gcc8_temp)
# print(marchs_families['apple-clang'][9.1] == marchs_families_apple91_temp)


# --------------------------------------------------------------------------------


# GCC7 no tiene: knm, cannonlake, icelake-client, icelake-server
# GCC6 no tiene: ninguno de los VIA que tenemos
# GCC5 no tiene: skylake, skylake-avx512, znver1
# GCC4 no tiene: knl

# Apple LLVM version 9.1.0 (clang-902.0.39.1)
    # icelake-client
    # icelake-server
    # goldmont-plus
    # tremont
    # knm
    # eden-x2
    # eden-x4
    # nano
    # nano-1000
    # nano-2000
    # nano-3000
    # nano-x2
    # nano-x4



# https://gcc.gnu.org/onlinedocs/

    # https://gcc.gnu.org/onlinedocs/gcc/x86-Options.html
    # echo "" | gcc -fsyntax-only -march=pepe -xc -
    # nocona core2 nehalem corei7 westmere sandybridge corei7-avx ivybridge core-avx-i haswell core-avx2 broadwell skylake skylake-avx512 bonnell atom silvermont slm knl x86-64 eden-x2 nano nano-1000 nano-2000 nano-3000 nano-x2 eden-x4 nano-x4 k8 k8-sse3 opteron opteron-sse3 athlon64 athlon64-sse3 athlon-fx amdfam10 barcelona bdver1 bdver2 bdver3 bdver4 znver1 btver1 btver2


# g++ --version
# g++ (Ubuntu 7.3.0-16ubuntu3~16.04.1) 7.3.0
# Copyright (C) 2017 Free Software Foundation, Inc.
# This is free software; see the source for copying conditions.  There is NO
# warranty; not even for MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
 
# echo "" | gcc -fsyntax-only -march=pepe -xc -
# cc1: note: valid arguments to '-march=' switch are: nocona core2 nehalem corei7 westmere sandybridge corei7-avx ivybridge core-avx-i haswell core-avx2 broadwell skylake skylake-avx512 bonnell atom silvermont slm knl x86-64 eden-x2 nano nano-1000 nano-2000 nano-3000 nano-x2 eden-x4 nano-x4 k8 k8-sse3 opteron opteron-sse3 athlon64 athlon64-sse3 athlon-fx amdfam10 barcelona bdver1 bdver2 bdver3 bdver4 znver1 btver1 btver2


# echo "" | clang -fsyntax-only -march=x86-64 -xc -




# clang --version
# Apple LLVM version 9.1.0 (clang-902.0.39.1)
# Target: x86_64-apple-darwin17.6.0
# Thread model: posix
# InstalledDir: /Applications/Xcode.app/Contents/Developer/Toolchains/XcodeDefault.xctoolchain/usr/bin



# Kaby Lake
#     Successor	
#         Desktop: Coffee Lake (2nd Optimization)
#                  Whiskey Lake (3rd Optimization)
#         Mobile:  Cannon Lake (Process)
#         Servers and Desktop: Cascade Lake (3rd Optimization)[4][5]

# Coffee Lake
#     Successor	
#         Desktop:    Whiskey Lake (3rd Optimization)
#         Mobile:     Cannon Lake (Process)
#         Ice Lake (Architecture)

# Whiskey Lake
#     Successor
# 	    Cannon Lake (Process)
#         Ice Lake (Architecture)

# Cannon Lake (Skymont)
#     Successor
#         Ice Lake (Architecture)

# Cascade Lake
#     Successor
#         Ice Lake (Architecture)

# Ice Lake
#     Successor
#     	Tiger Lake (Optimization)

# Tiger Lake
#     Successor	
#         Sapphire Rapids (unknown)

# Sapphire Rapids
#     Successor	

# Linea Knights
#     Polaris | Larrabee (LRB) | Rock Creek
#     Knights Ferry (KNF) 
#     Knights Corner (KNC) 
#     Knights Landing (KNL) | Knights Mill (KNM)
#     Knights Hill (KNH)
#     Knights Peak (KNP)

# Linea Atom
#     Bonnell         x86-64, MOVBE, MMX, SSE, SSE2, SSE3, SSSE3
#     Saltwell        x86-64, MOVBE, MMX, SSE, SSE2, SSE3, SSSE3
#     Silvermont      x86-64, MOVBE, MMX, SSE, SSE2, SSE3, SSSE3, SSE4.1, SSE4.2, POPCNT, AES, PCLMUL, RDRND
#     Airmont         x86-64, MOVBE, MMX, SSE, SSE2, SSE3, SSSE3, SSE4.1, SSE4.2, POPCNT, AES, PCLMUL, RDRND
#     Goldmont        x86-64, MOVBE, MMX, SSE, SSE2, SSE3, SSSE3, SSE4.1, SSE4.2, POPCNT, AES, PCLMUL, RDRND, SHA
#     Goldmont Plus   x86-64, MOVBE, MMX, SSE, SSE2, SSE3, SSSE3, SSE4.1, SSE4.2, POPCNT, AES, PCLMUL, RDRND, SHA
#     Tremont         x86-64, MOVBE, MMX, SSE, SSE2, SSE3, SSSE3, SSE4.1, SSE4.2, POPCNT, AES, PCLMUL, RDRND, SHA
