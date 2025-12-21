import re
from typing import Any
import hbctool
import tempfile
ALWAYS_TRUE = [('LoadConstTrue', [('Reg8', False, 0)]), ('Ret', [('Reg8', False, 0)])]
ALWAYS_FALSE = [('LoadConstFalse', [('Reg8', False, 0)]), ('Ret', [('Reg8', False, 0)])]
ALWAYS_UNDEFINED = [('LoadConstUndefined', [('Reg8', False, 0)]), ('Ret', [('Reg8', False, 0)])]
EMPTY_OBJECT = [('NewObject', [('Reg8', False, 0)]), ('Ret', [('Reg8', False, 0)])]

class KindleHBC:
    def __init__(self, path: str) -> None:
        self.out_path = tempfile.mkdtemp(prefix="KindleHBC")
        f = open(path, "rb")
        self.hbcs = hbctool.hbc.load(f)
        print(f"HBC Version {self.hbcs.getVersion()}")
        print(self.hbcs.getVersion())
        self.hbcs.setFunction

        pass

    def find_func_by_name(self, name, disasm=True):
        for x in range(self.hbcs.getFunctionCount()):
            fnName = self.hbcs.getString(self.hbcs.getObj()["functionHeaders"][x]["functionName"])[0]
            if name in fnName:
                return (x, self.hbcs.getFunction(x, disasm))
        return (-1, None)

    def replace_func(self, fid, func, new_func):
        fun_new = list(func)
        fun_new[4] = new_func
        self.hbcs.setFunction(fid, fun_new)
        pass

    def check_func_patch(self, fid, patch) -> bool:
        fun = self.hbcs.getFunction(fid, disasm = True)
        return fun[4] == patch

    def check_string_patch(self, sid, patch) -> bool:
        string, _ = self.hbcs.getString(sid)
        return string.strip("\0") == patch

    def patch_func(self, function_name: str, patch: Any) -> bool:
        print(f"Patching {function_name}.")
        (fid, fun) = self.find_func_by_name(function_name)
        return self.patch_func_by_id(fid, fun, patch)
    
    def patch_func_by_id(self, fid: int, fun: Any, patch: Any) -> bool:
        if fid < 0:
            print(f"Function not found!")
            return False
        self.replace_func(fid, fun, patch)
        if (self.check_func_patch(fid, patch)):
            print("Patch successful!")
            return True
        print("Unknown error!")
        return False    

    def find_strings_regex(self, regex: str, min_len = 0) -> list[tuple[int, int, str]]:
        strings = []
        compiled = re.compile(regex)
        for sid in range(self.hbcs.getStringCount()):
            s, info = self.hbcs.getString(sid)
            if compiled.match(s):
                if (len(s) >= min_len):
                    # print(s, sid, info)
                    strings.append((sid, len(s), s))
        return strings

    def find_string(self, string: str) -> int:
        for sid in range(self.hbcs.getStringCount()):
            s, info = self.hbcs.getString(sid)
            if string == s:
                # print(s, sid, info)
                return sid
        return -1

    def replace_string(self, orig: str, patched: str) -> int:
        sid = self.find_string(orig)
        if (sid < 0):
            return sid
        self.hbcs.setString(sid, patched)
        return sid

    def replace_string_regex(self, regex: str, patched: str) -> list[tuple[int, int, str]]:
        sids = self.find_strings_regex(regex, len(patched))
        if (sids == []):
            return sids
        for (sid, l, _) in sids:
            self.hbcs.setString(sid, patched + "\0" * (l - len(patched)))
        return sids


    def replace_string_ref_in_func(self, fid, og_sid, patch_sid) -> bool:
        fun = self.hbcs.getFunction(fid)
        insts = fun[4]
        for x in insts:
            if x[0] == "GetById":
                if x[1][3][2] == og_sid:
                    x[1][3] = list(x[1][3])
                    x[1][3][2] = patch_sid
                    x[1][3] = tuple(x[1][3])
        return self.patch_func_by_id(fid, fun, insts)


    def patch_string_regex(self, regex: str, patched: str) -> bool:
        # if (len(orig) != len(patched)):
        #     raise Exception("Length of orig and patch must be the same!")
        sids = self.replace_string_regex(regex, patched)
        if (len(sids) == 0):
            print(f"Regex '{regex}' not found")
            return False
        i = 0
        for (sid, _, s) in sids:
            i += 1
            if (self.check_string_patch(sid, patched)):
                print(f"[{s}->{patched}] - Regex string patch successful!")
            else:
                print(f"[{s}->{patched}] - Regex string patch failed!")
        return True

    def patch_string(self, orig: str, patched: str) -> bool:
        if (len(orig) != len(patched)):
            raise Exception(f"Length of orig {orig}:{len(orig)} and patch {patched}:{len(patched)} must be the same!")
        sid = self.replace_string(orig, patched)
        if (sid < 0):
            print(f"String '{orig}' not found")
            return False
            
        if (self.check_string_patch(sid, patched)):
            print(f"[{orig}->{patched}] String patch successful!")
            return True
        print(f"[{orig}->{patched}] String patch failed!")
        return False

    def null_string(self, orig: str) -> bool:
        return self.patch_string(orig, " " * len(orig))

    def dump(self, path: str) -> None:
        with open(path, "wb+") as f:
            hbctool.hbc.dump(self.hbcs, f)

def patch_registration_detection(khbc: KindleHBC):
    print("Patching registration!")
    khbc.patch_func("checkDeviceRegistration", ALWAYS_UNDEFINED)
    khbc.patch_func("IsDeviceRegistered", ALWAYS_TRUE)
    khbc.patch_func("isDeviceRegistered", ALWAYS_TRUE)

def patch_store_button(khbc: KindleHBC):
    print("Patching store!")
    khbc.patch_func("storeButton", EMPTY_OBJECT)
    khbc.null_string("com.lab126.store")
    khbc.null_string("KPP_STORE")
    khbc.null_string("chrome.topnavbar.button.open_store")
    khbc.null_string("com.lab126.KPPStoreShopping")
    khbc.null_string("cart-filled")
    khbc.patch_func("isStoreLocked", ALWAYS_TRUE)

# def patch_home_to_library(khbc: KindleHBC):
#     print("Removing home tab")
#     fid, _ = khbc.find_func_by_name("navigateToHome")
#     fid2, _ = khbc.find_func_by_name("shouldResetViewState")
#     kpp_home = khbc.find_string("KPP_HOME")
#     kpp_library = khbc.find_string("KPP_LIBRARY")
#     khbc.replace_string_ref_in_func(fid, kpp_home, kpp_library)
#     khbc.replace_string_ref_in_func(fid2, kpp_home, kpp_library)
	# CreateClosure       	Reg8:1, Reg8:1, UInt16:15746
    # patch = [('CreateClosure', [('Reg8', False, 1, fid)]), ]
    # khbc.patch_func("navigateToHome", ALWAYS_UNDEFINED)

def patch_homepage(khbc: KindleHBC):
    print("Patching homepage content!")
    khbc.patch_string_regex("Template(\\d*)Card", "Template0Card")
    # for x in replace_me:

        # khbc.patch_string(x, patch + '\0' * (len(x) - len(patch)))

def main():
    print("KPP_Patch running!")
    khbc = KindleHBC("./KPPMainApp.js.hbc")
    patch_registration_detection(khbc)
    patch_homepage(khbc)
    patch_store_button(khbc)
    # patch_home_to_library(khbc)
    khbc.dump("./KPPMainApp.js.hbc.patched")


if __name__ == "__main__":
    main()
