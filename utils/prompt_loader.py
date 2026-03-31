from utils.config_handler import prompts_conf
from utils.path_tool import get_abs_path
from utils.logger_handler import logger


def load_wajue_prompts():
    try:
        wajue_prompt_path = get_abs_path(prompts_conf["wajue_prompt_path"])
    except KeyError as e:
        logger.error(f"[load_system_prompts]在yaml配置项中没有wajue_prompt_path配置项")
        raise e

    try:
        return open(wajue_prompt_path, "r", encoding="utf-8").read()
    except Exception as e:
        logger.error(f"[wajue_prompt_path]解析系统提示词出错，{str(e)}")
        raise e


def load_gongbiao_prompts():
    try:
        gongbiao_prompt_path = get_abs_path(prompts_conf["gongbiao_prompt_path"])
    except KeyError as e:
        logger.error(f"[load_system_prompts]在yaml配置项中没有gongbiao_prompt_path配置项")
        raise e

    try:
        return open(gongbiao_prompt_path, "r", encoding="utf-8").read()
    except Exception as e:
        logger.error(f"[gongbiao_prompt_path]解析系统提示词出错，{str(e)}")
        raise e

def load_jinggai_prompts():
    try:
        jinggai_prompt_path = get_abs_path(prompts_conf["jinggai_prompt_path"])
    except KeyError as e:
        logger.error(f"[load_system_prompts]在yaml配置项中没有jinggai_prompt_path配置项")
        raise e

    try:
        return open(jinggai_prompt_path, "r", encoding="utf-8").read()
    except Exception as e:
        logger.error(f"[jinggai_prompt_path]解析系统提示词出错，{str(e)}")
        raise e

def load_xuangua_prompts():
    try:
        xuangua_prompt_path = get_abs_path(prompts_conf["xuangua_prompt_path"])
    except KeyError as e:
        logger.error(f"[load_system_prompts]在yaml配置项中没有xuangua_prompt_path配置项")
        raise e

    try:
        return open(xuangua_prompt_path, "r", encoding="utf-8").read()
    except Exception as e:
        logger.error(f"[xuangua_prompt_path]解析系统提示词出错，{str(e)}")
        raise e

def load_duifang_prompts():
    try:
        duifang_prompt_path = get_abs_path(prompts_conf["duifang_prompt_path"])
    except KeyError as e:
        logger.error(f"[load_system_prompts]在yaml配置项中没有duifang_prompt_path配置项")
        raise e

    try:
        return open(duifang_prompt_path, "r", encoding="utf-8").read()
    except Exception as e:
        logger.error(f"[duifang_prompt_path]解析系统提示词出错，{str(e)}")
        raise e

def load_baitai_prompts():
    try:
        baitai_prompt_path = get_abs_path(prompts_conf["baitai_prompt_path"])
    except KeyError as e:
        logger.error(f"[load_system_prompts]在yaml配置项中没有baitai_prompt_path配置项")
        raise e

    try:
        return open(baitai_prompt_path, "r", encoding="utf-8").read()
    except Exception as e:
        logger.error(f"[baitai_prompt_path]解析系统提示词出错，{str(e)}")
        raise e

if __name__ == '__main__':
    print(load_baitai_prompts())

