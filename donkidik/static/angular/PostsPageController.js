angular.module('DonkidikApp')
	.controller('PostsPageController', function($scope, postsService){
		console.log('in controller');
		// properties
		$scope.posts = [];
		$scope.types = [];

		// methods
		$scope.get_types = function(){
			postsService.get_types().then(function(res){
				$scope.types = res.data;
			});

		};
		$scope.get_posts_from_server = function(){
			postsService.get_posts_from_server().then(function(res){
				$scope.posts = res.data;
			});
		};
		
		$scope.add_post_comment = function(pid, text){
			if (text == '' || text == null){
				alert("can't comment with no text")
				return;
			}
			postsService.add_post_comment(pid, text).then(function(res){
				if (res.status=='OK'){
					$scope.get_posts_from_server();
				}
				else{
					// TODO communicate this to UI
					alert("something went wrong...");
				}
			});
		}

		$scope.change_more = function(post){
			if (post.more){
				post.more = false;
			}else{
				post.more = true;
			}
		};
		
		// first calls
		// $scope.get_types(); TODO not sure how to resolve this
		$scope.get_posts_from_server();





	});