import logging
import re
import tempfile
from typing import Any, cast

from hbctool import hbc

logger = logging.getLogger(__name__)


class KindleHBC:
    def __init__(self, path: str) -> None:
        self.out_path = tempfile.mkdtemp(prefix="KindleHBC")
        f = open(path, "rb")
        self.hbcs = cast(hbc.HBCBase, hbc.load(f))
        logger.info(f"HBC Version {self.hbcs.getVersion()}")

    def find_func_by_name(
        self,
        name: str,
        disasm: bool = True,
    ) -> tuple[int, hbc.FuncUnion | None]:
        for x in range(self.hbcs.getFunctionCount()):
            fnName = self.hbcs.getString(
                self.hbcs.getObj()["functionHeaders"][x]["functionName"]
            )[0]
            if name in fnName:
                return (x, self.hbcs.getFunction(x, disasm))
        return (-1, None)

    def replace_func(
        self,
        fid: int,
        func: hbc.FuncUnion,
        new_insts: list[int] | list[hbc.InstructionDisassembled],
    ) -> None:
        fun_new = func._replace(instructions=new_insts)  # type: ignore[arg-type]
        self.hbcs.setFunction(fid, fun_new)

    def check_func_patch(
        self, fid: int, patch: list[hbc.InstructionDisassembled]
    ) -> bool:
        fun = self.hbcs.getDisassembledFunction(fid=fid)
        return fun[4] == patch

    def check_string_patch(self, sid: int, patch: Any) -> bool:
        string, _ = self.hbcs.getString(sid)
        return string.strip("\0") == patch

    def patch_func(self, function_name: str, patch: Any) -> bool:
        logger.info(f"Patching {function_name}.")
        fid, fun = self.find_func_by_name(function_name)
        return self.patch_func_by_id(fid, fun, patch)

    def patch_func_by_id(self, fid: int, fun: Any, patch: Any) -> bool:
        if fid < 0:
            logger.info(f"Function not found!")
            return False
        self.replace_func(fid, fun, patch)
        if self.check_func_patch(fid, patch):
            logger.info("Patch successful!")
            return True
        logger.info("Unknown error!")
        return False

    def find_strings_regex(
        self, regex: str, min_len: int = 0
    ) -> list[tuple[int, int, str]]:
        strings = []
        compiled = re.compile(regex)
        for sid in range(self.hbcs.getStringCount()):
            s, info = self.hbcs.getString(sid)
            if compiled.match(s):
                if len(s) >= min_len:
                    # logger.info(s, sid, info)
                    strings.append((sid, len(s), s))
        return strings

    def find_string(self, string: str) -> int:
        for sid in range(self.hbcs.getStringCount()):
            s, info = self.hbcs.getString(sid)
            if string == s:
                # logger.info(s, sid, info)
                return sid
        return -1

    def replace_string(self, orig: str, patched: str) -> int:
        sid = self.find_string(orig)
        if sid < 0:
            return sid
        self.hbcs.setString(sid, patched)
        return sid

    def replace_string_regex(
        self, regex: str, patched: str
    ) -> list[tuple[int, int, str]]:
        sids = self.find_strings_regex(regex, len(patched))
        if sids == []:
            return sids
        for sid, l, _ in sids:
            self.hbcs.setString(sid, patched + "\0" * (l - len(patched)))
        return sids

    def replace_string_ref_in_func(self, fid: int, og_sid: int, patch_sid: int) -> bool:
        fun = self.hbcs.getDisassembledFunction(fid=fid)
        insts = fun.instructions
        for x in insts:
            if x.instruction == "GetById" and x.arguments[3].arg_value == og_sid:
                x.arguments[3]._replace(arg_value=patch_sid)
        return self.patch_func_by_id(fid, fun, insts)

    def patch_string_regex(self, regex: str, patched: str) -> bool:
        # if (len(orig) != len(patched)):
        #     raise Exception("Length of orig and patch must be the same!")
        sids = self.replace_string_regex(regex, patched)
        if len(sids) == 0:
            logger.info(f"Regex '{regex}' not found")
            return False
        i = 0
        for sid, _, s in sids:
            i += 1
            if self.check_string_patch(sid, patched):
                logger.info(f"[{s}->{patched}] - Regex string patch successful!")
            else:
                logger.info(f"[{s}->{patched}] - Regex string patch failed!")
        return True

    def patch_string(self, orig: str, patched: str) -> bool:
        if len(orig) != len(patched):
            raise Exception(
                f"Length of orig {orig}:{len(orig)} and "
                f"patch {patched}:{len(patched)} must be the same!"
            )
        sid = self.replace_string(orig, patched)
        if sid < 0:
            logger.info(f"String '{orig}' not found")
            return False

        if self.check_string_patch(sid, patched):
            logger.info(f"[{orig}->{patched}] String patch successful!")
            return True
        logger.info(f"[{orig}->{patched}] String patch failed!")
        return False

    def null_string(self, orig: str) -> bool:
        return self.patch_string(orig, " " * len(orig))

    def dump(self, path: str) -> None:
        with open(path, "wb+") as f:
            hbc.dump(self.hbcs, f)
