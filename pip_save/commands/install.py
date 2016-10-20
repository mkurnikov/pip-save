from pip import cmdoptions
from pip.commands import InstallCommand
from pip.req import InstallRequirement

from pip_save.save_cmdoptions import save
from pip_save.save_cmdoptions import save_dev


class MyInstallCommand(InstallCommand):
    name = 'install'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        save_group = {
            'name': 'Metadata File Options',
            'options': [
                save,
                save_dev
            ]
        }

        save_opts = cmdoptions.make_option_group(
            save_group,
            self.parser,
        )

        self.parser.insert_option_group(0, save_opts)

    def run(self, options, args):
        if options.save:
            print('--save specified')

        if options.save_dev:
            print('--save-dev specified')

        packages_to_install = args
        requirements_from_args = []
        for install_req_line in packages_to_install:
            requirements_from_args.append(InstallRequirement.from_line(install_req_line))

        from pprint import pprint
        pprint(requirements_from_args)
        # print(requirements_from_args)
        # move to packaging/pkg_resources
        # installed_dists_before = list(working_set)
        # dist_path = DistributionPath(include_egg=True)
        # installed_dists_before = list(dist_path.get_distributions())

        # status = 0
        status = super().run(options, args)
        # print(status)

        # update working set
        # pkg_resources._initialize_master_working_set()
        # installed_dists_after = list(working_set)

        # dist_path = DistributionPath(include_egg=True)
        # installed_dists_after = list(dist_path.get_distributions())

        # diff = []  # type: List[InstalledDistribution]
        # for dist in installed_dists_after:
        #     if dist not in installed_dists_before:
        #         diff.append(dist)
        #
        # requested_installed_dists = []
        # for idist in diff:
        #     for req in requirements_from_args:
        #         name = canonicalize_name(req.name)
        #         if name == canonicalize_name(idist.metadata.name):
        #             requested_installed_dists.append(idist)
        #             break

        # pprint(requested_installed_dists)

        # diff = installed_dists_after - installed_dists_before
        # from pprint import pprint
        # pprint(diff)

        # print(len(installed_dists_before))
        # print(len(installed_dists_after))

        return status
