
/*
 * Copyright (C) Ogal Optronics Systems Ltd.
 *
 * Author: Sebastian Cabot
 *
 *
 * Your desired license
 *  
 */

#include <cstdlib>
#include <cstdio>
#include <cerrno>
#include <iostream>
#include <fstream>

#include <atomic>
#include <vector>

#include "op.h"

extern "C"
{
#include <signal.h>
#include <argp.h>
#include <fcntl.h>
#include <unistd.h>
#include <sys/stat.h>
#include <sys/types.h>
}

namespace
{
    std::atomic<bool> g_stop(false);
    std::string g_ipcNmae;
    int g_log2Length = 2;
    bool g_dumpFiles = false;
    void sig_handler(int)
    {
        g_stop = true;
    }
}


using namespace std;

int main(int argc, char * argv[])
{
	// Opening pipe
	std::string sPipename = R"(/opt/eyerop/bin/camera.out)";

	ofstream op;
	int i = 0;
	while (i < 1000000){
		op.open(sPipename, ios::out);
		op <<  i << std::endl;
		op.close();
		i++;
	}

	if (!pipe)
	{
		std::cerr << "cannot open pipe to read" << endl;
		return 1;
	}
	return 1;

}

