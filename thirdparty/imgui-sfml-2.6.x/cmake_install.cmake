# Install script for directory: /home/rage/Projects/SFMLCmakeSetup-master/thirdparty/imgui-sfml-2.6.x

# Set the install prefix
if(NOT DEFINED CMAKE_INSTALL_PREFIX)
  set(CMAKE_INSTALL_PREFIX "/usr/local")
endif()
string(REGEX REPLACE "/$" "" CMAKE_INSTALL_PREFIX "${CMAKE_INSTALL_PREFIX}")

# Set the install configuration name.
if(NOT DEFINED CMAKE_INSTALL_CONFIG_NAME)
  if(BUILD_TYPE)
    string(REGEX REPLACE "^[^A-Za-z0-9_]+" ""
           CMAKE_INSTALL_CONFIG_NAME "${BUILD_TYPE}")
  else()
    set(CMAKE_INSTALL_CONFIG_NAME "")
  endif()
  message(STATUS "Install configuration: \"${CMAKE_INSTALL_CONFIG_NAME}\"")
endif()

# Set the component getting installed.
if(NOT CMAKE_INSTALL_COMPONENT)
  if(COMPONENT)
    message(STATUS "Install component: \"${COMPONENT}\"")
    set(CMAKE_INSTALL_COMPONENT "${COMPONENT}")
  else()
    set(CMAKE_INSTALL_COMPONENT)
  endif()
endif()

# Install shared libraries without execute permission?
if(NOT DEFINED CMAKE_INSTALL_SO_NO_EXE)
  set(CMAKE_INSTALL_SO_NO_EXE "0")
endif()

# Is this installation the result of a crosscompile?
if(NOT DEFINED CMAKE_CROSSCOMPILING)
  set(CMAKE_CROSSCOMPILING "FALSE")
endif()

# Set path to fallback-tool for dependency-resolution.
if(NOT DEFINED CMAKE_OBJDUMP)
  set(CMAKE_OBJDUMP "/usr/bin/objdump")
endif()

if(CMAKE_INSTALL_COMPONENT STREQUAL "Unspecified" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/lib64" TYPE STATIC_LIBRARY FILES "/home/rage/Projects/SFMLCmakeSetup-master/thirdparty/imgui-sfml-2.6.x/libImGui-SFML.a")
endif()

if(CMAKE_INSTALL_COMPONENT STREQUAL "Unspecified" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/include" TYPE FILE FILES
    "/home/rage/Projects/SFMLCmakeSetup-master/thirdparty/imgui-sfml-2.6.x/imgui-SFML.h"
    "/home/rage/Projects/SFMLCmakeSetup-master/thirdparty/imgui-sfml-2.6.x/imgui-SFML_export.h"
    "/home/rage/Projects/SFMLCmakeSetup-master/thirdparty/imgui-docking/imgui/imconfig.h"
    "/home/rage/Projects/SFMLCmakeSetup-master/thirdparty/imgui-docking/imgui/imgui.h"
    "/home/rage/Projects/SFMLCmakeSetup-master/thirdparty/imgui-docking/imgui/imgui_internal.h"
    "/home/rage/Projects/SFMLCmakeSetup-master/thirdparty/imgui-docking/imgui/imstb_rectpack.h"
    "/home/rage/Projects/SFMLCmakeSetup-master/thirdparty/imgui-docking/imgui/imstb_textedit.h"
    "/home/rage/Projects/SFMLCmakeSetup-master/thirdparty/imgui-docking/imgui/imstb_truetype.h"
    "/home/rage/Projects/SFMLCmakeSetup-master/thirdparty/imgui-docking/imgui/misc/cpp/imgui_stdlib.h"
    "/home/rage/Projects/SFMLCmakeSetup-master/thirdparty/imgui-sfml-2.6.x/imconfig-SFML.h"
    )
endif()

if(CMAKE_INSTALL_COMPONENT STREQUAL "Unspecified" OR NOT CMAKE_INSTALL_COMPONENT)
  if(EXISTS "$ENV{DESTDIR}${CMAKE_INSTALL_PREFIX}/lib64/cmake/ImGui-SFML/ImGui-SFMLConfig.cmake")
    file(DIFFERENT _cmake_export_file_changed FILES
         "$ENV{DESTDIR}${CMAKE_INSTALL_PREFIX}/lib64/cmake/ImGui-SFML/ImGui-SFMLConfig.cmake"
         "/home/rage/Projects/SFMLCmakeSetup-master/thirdparty/imgui-sfml-2.6.x/CMakeFiles/Export/3d81db8e277c760ab8b6bed07c34c449/ImGui-SFMLConfig.cmake")
    if(_cmake_export_file_changed)
      file(GLOB _cmake_old_config_files "$ENV{DESTDIR}${CMAKE_INSTALL_PREFIX}/lib64/cmake/ImGui-SFML/ImGui-SFMLConfig-*.cmake")
      if(_cmake_old_config_files)
        string(REPLACE ";" ", " _cmake_old_config_files_text "${_cmake_old_config_files}")
        message(STATUS "Old export file \"$ENV{DESTDIR}${CMAKE_INSTALL_PREFIX}/lib64/cmake/ImGui-SFML/ImGui-SFMLConfig.cmake\" will be replaced.  Removing files [${_cmake_old_config_files_text}].")
        unset(_cmake_old_config_files_text)
        file(REMOVE ${_cmake_old_config_files})
      endif()
      unset(_cmake_old_config_files)
    endif()
    unset(_cmake_export_file_changed)
  endif()
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/lib64/cmake/ImGui-SFML" TYPE FILE FILES "/home/rage/Projects/SFMLCmakeSetup-master/thirdparty/imgui-sfml-2.6.x/CMakeFiles/Export/3d81db8e277c760ab8b6bed07c34c449/ImGui-SFMLConfig.cmake")
  if(CMAKE_INSTALL_CONFIG_NAME MATCHES "^()$")
    file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/lib64/cmake/ImGui-SFML" TYPE FILE FILES "/home/rage/Projects/SFMLCmakeSetup-master/thirdparty/imgui-sfml-2.6.x/CMakeFiles/Export/3d81db8e277c760ab8b6bed07c34c449/ImGui-SFMLConfig-noconfig.cmake")
  endif()
endif()

string(REPLACE ";" "\n" CMAKE_INSTALL_MANIFEST_CONTENT
       "${CMAKE_INSTALL_MANIFEST_FILES}")
if(CMAKE_INSTALL_LOCAL_ONLY)
  file(WRITE "/home/rage/Projects/SFMLCmakeSetup-master/thirdparty/imgui-sfml-2.6.x/install_local_manifest.txt"
     "${CMAKE_INSTALL_MANIFEST_CONTENT}")
endif()
